from ninja import Schema
from typing import Optional
from datetime import datetime
from .users_schema import UserSchema

class ResponseSchemaIn(Schema):
    message: str
    proposed_price: Optional[float] = None

class ResponseSchemaOut(Schema):
    id: int
    message: str
    proposed_price: Optional[float]
    status: str
    created_at: datetime
    worker: UserSchema
    repair_request_id: int

    @staticmethod
    def resolve_worker(obj):
        return UserSchema.from_orm(obj.worker)
