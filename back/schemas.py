# api/schemas.py
from ninja import Schema
from typing import Optional, List
from datetime import date, datetime

class Message(Schema):
    message: str

class UserSchema(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str

class UserCreate(Schema):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_type: str  # 'customer' или 'worker'

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

# Схемы для откликов
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

class LoginInput(Schema):
    username: str
    password: str

class TokenOutput(Schema):
    access: str
    refresh: str