from datetime import datetime

from ninja import Schema

from back.schemas import UserSchema


class ChatMessageSchemaIn(Schema):
    message: str

class ChatMessageSchemaOut(Schema):
    id: int
    message: str
    sender: UserSchema
    created_at: datetime
    is_read: bool

    @staticmethod
    def resolve_sender(obj):
        return UserSchema.from_orm(obj.sender)