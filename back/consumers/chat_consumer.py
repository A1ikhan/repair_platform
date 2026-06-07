import json
import logging
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from back.models import RepairRequest, Response
from back.models.chat_model import ChatMessage
from back.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.repair_request_id = int(self.scope['url_route']['kwargs']['repair_request_id'])
        self.room_group_name = f'chat_{self.repair_request_id}'

        user = await self._authenticate()
        if user is None:
            await self.close(code=4001)
            return

        self.user = user

        if not await self._has_access():
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, ValueError):
            return

        msg_type = data.get('type', 'message')

        if msg_type == 'message':
            text = data.get('message', '').strip()
            if not text:
                return
            message = await self._save_message(text)
            await self._send_notification(message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.message',
                    'id': message.id,
                    'message': message.message,
                    'sender_id': self.user.id,
                    'sender_username': self.user.username,
                    'created_at': message.created_at.isoformat(),
                    'is_read': False,
                }
            )

        elif msg_type == 'mark_read':
            await self._mark_as_read()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.read',
                    'user_id': self.user.id,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'id': event['id'],
            'message': event['message'],
            'sender': {
                'id': event['sender_id'],
                'username': event['sender_username'],
            },
            'created_at': event['created_at'],
            'is_read': event['is_read'],
        }))

    async def chat_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'user_id': event['user_id'],
        }))

    # ── helpers ──────────────────────────────────────────────────────────────

    @database_sync_to_async
    def _authenticate(self):
        qs = parse_qs(self.scope.get('query_string', b'').decode())
        token_list = qs.get('token')
        if not token_list:
            return None
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            token = AccessToken(token_list[0])
            return User.objects.select_related(
                'worker_profile', 'customer_profile'
            ).get(id=token['user_id'])
        except Exception:
            return None

    @database_sync_to_async
    def _has_access(self):
        try:
            rr = RepairRequest.objects.get(id=self.repair_request_id)
            if rr.created_by_id == self.user.id:
                return True
            return Response.objects.filter(
                repair_request_id=self.repair_request_id,
                worker=self.user,
            ).exists()
        except RepairRequest.DoesNotExist:
            return False

    @database_sync_to_async
    def _save_message(self, text: str) -> ChatMessage:
        return ChatMessage.objects.create(
            repair_request_id=self.repair_request_id,
            sender=self.user,
            message=text,
        )

    @database_sync_to_async
    def _mark_as_read(self):
        ChatMessage.objects.filter(
            repair_request_id=self.repair_request_id,
        ).exclude(sender=self.user).update(is_read=True)

    @database_sync_to_async
    def _send_notification(self, message: ChatMessage):
        try:
            rr = RepairRequest.objects.select_related('created_by').get(
                id=self.repair_request_id
            )
            if self.user.id == rr.created_by_id:
                accepted = Response.objects.filter(
                    repair_request=rr, status='accepted'
                ).select_related('worker').first()
                if accepted:
                    recipient = accepted.worker
                else:
                    return
            else:
                recipient = rr.created_by

            NotificationService.create_notification(
                recipient,
                f"Новое сообщение в чате по заявке '{rr.title}'",
                'new_message',
            )
        except Exception as e:
            logger.warning("Could not send chat notification: %s", e)
