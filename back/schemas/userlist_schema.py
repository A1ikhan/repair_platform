from datetime import datetime
from typing import Optional, List

from ninja import Schema
from pydantic import field_validator

from back.schemas import RepairRequestSchemaOut

_VALID_LIST_TYPES = {'favorite', 'watching', 'applied', 'completed'}


class UserListSchemaIn(Schema):
    name: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v not in _VALID_LIST_TYPES:
            raise ValueError(f"name must be one of: {', '.join(sorted(_VALID_LIST_TYPES))}")
        return v

class UserListSchemaOut(Schema):
    id: int
    name: str
    display_name: str
    item_count: int
    created_at: datetime

    @staticmethod
    def resolve_display_name(obj):
        return obj.get_name_display()

    @staticmethod
    def resolve_item_count(obj):
        # Use len() to hit the prefetch_related cache instead of issuing a COUNT query
        return len(obj.items.all())

class ListItemSchemaIn(Schema):
    repair_request_id: int
    notes: Optional[str] = None

class ListItemSchemaOut(Schema):
    id: int
    repair_request: RepairRequestSchemaOut
    added_at: datetime
    notes: Optional[str]

    @staticmethod
    def resolve_repair_request(obj):
        return RepairRequestSchemaOut.from_orm(obj.repair_request)

class UserListDetailSchema(Schema):
    list_info: UserListSchemaOut
    items: List[ListItemSchemaOut]