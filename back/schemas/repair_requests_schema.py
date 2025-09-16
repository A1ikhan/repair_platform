from ninja import Schema
from typing import Optional
from datetime import date, datetime
from .users_schema import UserSchema

class RepairRequestSchemaIn(Schema):
    title: str
    description: str
    device_type: str
    address: str
    desired_completion_date: Optional[date] = None

class RepairRequestSchemaOut(Schema):
    id: int
    title: str
    description: str
    device_type: str
    address: str
    desired_completion_date: Optional[date] = None
    status: str
    created_by: UserSchema
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_created_by(obj):
        return UserSchema.from_orm(obj.created_by)
