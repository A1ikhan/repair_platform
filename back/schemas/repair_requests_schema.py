from ninja import Schema
from typing import Optional, List
from datetime import date, datetime
from .users_schema import UserSchema

class RepairRequestSchemaIn(Schema):
    title: str
    description: str
    device_type: str
    address: str
    desired_completion_date: Optional[date] = None

class FileSchemaOut(Schema):
    id: int
    file_url: str
    description: str
    uploaded_by: UserSchema
    uploaded_at: datetime

    @staticmethod
    def resolve_file_url(obj):
        return obj.file.url

    @staticmethod
    def resolve_uploaded_by(obj):
        return UserSchema.from_orm(obj.uploaded_by)

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
    files: List[FileSchemaOut] = []
    @staticmethod
    def resolve_created_by(obj):
        return UserSchema.from_orm(obj.created_by)

    @staticmethod
    def resolve_files(obj):
        return obj.files.all()