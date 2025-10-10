# Эндпоинты чата
from ninja import router

from back.schemas.chat_schema import ChatMessageSchemaOut, ChatMessageSchemaIn
from back.services.chat_service import ChatService


@router.post("/chat/request/{repair_request_id}", response=ChatMessageSchemaOut, auth=None)
def send_chat_message(request, repair_request_id: int, data: ChatMessageSchemaIn):
    """Send message in repair request chat"""
    return ChatService.send_message(repair_request_id, data.message, request.user)

@router.get("/chat/request/{repair_request_id}", response=list[ChatMessageSchemaOut], auth=None)
def get_chat_messages(request, repair_request_id: int):
    """Get chat messages for repair request"""
    return ChatService.get_chat_messages(repair_request_id, request.user)

@router.post("/chat/request/{repair_request_id}/read", response=dict, auth=None)
def mark_chat_as_read(request, repair_request_id: int):
    """Mark chat messages as read"""
    return ChatService.mark_messages_as_read(repair_request_id, request.user)