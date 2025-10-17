from datetime import datetime
from typing import Optional, List

from ninja import Schema

from back.schemas import RepairRequestSchemaOut


class UserListSchemaIn(Schema):
    name: str

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
        return obj.items.count()

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