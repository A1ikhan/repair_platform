# Эндпоинты чата
from ninja import Router

from back.schemas import ChatMessageSchemaOut, ChatMessageSchemaIn
from back.services import ChatService

router = Router(tags=["Chat"])

@router.post("/request/{repair_request_id}", response=ChatMessageSchemaOut)
def send_chat_message(request, repair_request_id: int, data: ChatMessageSchemaIn):
    """Send message in repair request chat"""
    return ChatService.send_message(repair_request_id, data.message, request.user)

@router.get("/request/{repair_request_id}", response=list[ChatMessageSchemaOut])
def get_chat_messages(request, repair_request_id: int):
    """Get chat messages for repair request"""
    return ChatService.get_chat_messages(repair_request_id, request.user)

@router.post("/request/{repair_request_id}/read", response=dict)
def mark_chat_as_read(request, repair_request_id: int):
    """Mark chat messages as read"""
    return ChatService.mark_messages_as_read(repair_request_id, request.user)


@router.get("/request/{repair_request_id}/unread", response=int)
def get_unread_count(request, repair_request_id: int):
    """Get count of unread messages"""
    from back.services import ChatService
    messages = ChatService.get_chat_messages(repair_request_id, request.user)
    unread_count = messages.exclude(sender=request.user).filter(is_read=False).count()
    return unread_count


@router.get("/unread", response=dict)
def get_all_unread_counts(request):
    """Get unread message counts for all user's chats"""
    from django.db.models import Count
    from back.models import RepairRequest, ChatMessage
    from django.db.models import Q

    # Получаем все заявки, где пользователь участвует в чате
    user_chats = RepairRequest.objects.filter(
        Q(created_by=request.user) |
        Q(responses__worker=request.user, responses__status='accepted')
    ).distinct()

    result = {}
    for chat in user_chats:
        unread_count = ChatMessage.objects.filter(
            repair_request=chat
        ).exclude(sender=request.user).filter(is_read=False).count()

        if unread_count > 0:
            result[chat.id] = unread_count

    return result