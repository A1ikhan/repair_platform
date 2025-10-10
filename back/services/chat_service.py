from ninja.errors import HttpError
from ninja.responses import Response

from back.models import RepairRequest
from back.models.chat_model import ChatMessage
from back.services.notification_service import NotificationService


class ChatService:
    @staticmethod
    def send_message(repair_request_id: int, message_text: str, sender):
        try:
            repair_request = RepairRequest.objects.get(id=repair_request_id)

            # Проверяем, что пользователь имеет доступ к чату
            if not ChatService._has_chat_access(repair_request, sender):
                raise HttpError(403, "No access to this chat")

            message = ChatMessage.objects.create(
                repair_request=repair_request,
                sender=sender,
                message=message_text
            )

            # Отправляем уведомление другому участнику
            ChatService._notify_new_message(repair_request, message, sender)

            return message

        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def _has_chat_access(repair_request, user):
        # Доступ имеют: автор заявки и принятый работник
        if user == repair_request.created_by:
            return True

        # Проверяем, есть ли принятый отклик от этого пользователя
        return Response.objects.filter(
            repair_request=repair_request,
            worker=user,
            status='accepted'
        ).exists()

    @staticmethod
    def _notify_new_message(repair_request, message, sender):
        # Определяем получателя уведомления
        if sender == repair_request.created_by:
            # Отправляем работнику
            accepted_response = Response.objects.filter(
                repair_request=repair_request,
                status='accepted'
            ).first()
            if accepted_response:
                recipient = accepted_response.worker
        else:
            # Отправляем автору заявки
            recipient = repair_request.created_by

        NotificationService.create_notification(
            recipient,
            f"Новое сообщение в чате по заявке '{repair_request.title}'",
            'new_message'
        )

    @staticmethod
    def get_chat_messages(repair_request_id: int, user):
        try:
            repair_request = RepairRequest.objects.get(id=repair_request_id)

            if not ChatService._has_chat_access(repair_request, user):
                raise HttpError(403, "No access to this chat")

            return ChatMessage.objects.filter(
                repair_request=repair_request
            ).select_related('sender').order_by('created_at')

        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def mark_messages_as_read(repair_request_id: int, user):
        try:
            repair_request = RepairRequest.objects.get(id=repair_request_id)

            if not ChatService._has_chat_access(repair_request, user):
                raise HttpError(403, "No access to this chat")

            # Помечаем все сообщения не от пользователя как прочитанные
            ChatMessage.objects.filter(
                repair_request=repair_request,
                sender__ne=user,
                is_read=False
            ).update(is_read=True)

            return {"message": "Messages marked as read"}

        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")