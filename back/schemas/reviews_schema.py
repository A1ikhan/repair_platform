from ninja import Schema
from typing import Optional
from datetime import datetime
from .users_schema import UserSchema

class ReviewSchemaIn(Schema):
    rating: int
    comment: Optional[str] = None

class ReviewSchemaOut(Schema):
    id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    customer: UserSchema
    worker: UserSchema

    @staticmethod
    def resolve_customer(obj):
        return UserSchema.from_orm(obj.customer)

    @staticmethod
    def resolve_worker(obj):
        return UserSchema.from_orm(obj.worker)
