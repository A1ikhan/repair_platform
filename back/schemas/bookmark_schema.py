from ninja import Schema
from typing import Optional, List
from datetime import datetime, date

from back.schemas import ResponseSchemaOut, UserSchema, RepairRequestSchemaOut


# Схемы для закладок
class BookmarkFolderSchema(Schema):
    id: int
    name: str
    color: str
    bookmark_count: int
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_bookmark_count(obj):
        return obj.bookmarks.count()

class BookmarkFolderCreate(Schema):
    name: str
    color: Optional[str] = '#3B82F6'

class BookmarkFolderUpdate(Schema):
    name: Optional[str] = None
    color: Optional[str] = None

class BookmarkSchema(Schema):
    id: int
    response: ResponseSchemaOut
    folder: Optional[BookmarkFolderSchema] = None
    priority: str
    priority_display: str
    status: str
    status_display: str
    planned_date: Optional[date] = None
    reminder_date: Optional[datetime] = None
    deadline: Optional[date] = None
    notes: str
    personal_rating: Optional[int] = None
    is_overdue: bool
    has_reminder: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_response(obj):
        return ResponseSchemaOut.from_orm(obj.response)

    @staticmethod
    def resolve_folder(obj):
        if obj.folder:
            return BookmarkFolderSchema.from_orm(obj.folder)
        return None

    @staticmethod
    def resolve_priority_display(obj):
        return obj.get_priority_display()

    @staticmethod
    def resolve_status_display(obj):
        return obj.get_status_display()

    @staticmethod
    def resolve_is_overdue(obj):
        return obj.is_overdue

    @staticmethod
    def resolve_has_reminder(obj):
        return obj.has_reminder

class BookmarkCreate(Schema):
    repair_request_id: int
    folder_id: Optional[int] = None
    priority: Optional[str] = 'medium'
    planned_date: Optional[date] = None
    reminder_date: Optional[datetime] = None
    deadline: Optional[date] = None
    notes: Optional[str] = None
    personal_rating: Optional[int] = None

class BookmarkUpdate(Schema):
    folder_id: Optional[int] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    planned_date: Optional[date] = None
    reminder_date: Optional[datetime] = None
    deadline: Optional[date] = None
    notes: Optional[str] = None
    personal_rating: Optional[int] = None

class BookmarkStatsSchema(Schema):
    total_bookmarks: int
    by_priority: dict
    by_status: dict
    overdue_count: int
    with_reminder_count: int
    completed_this_week: int

class BookmarkFilterSchema(Schema):
    folder_id: Optional[int] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    planned_date_from: Optional[date] = None
    planned_date_to: Optional[date] = None
    has_reminder: Optional[bool] = None
    is_overdue: Optional[bool] = None

# Обновляем схему Response чтобы включить информацию о закладках
class ResponseSchemaOut(Schema):
    id: int
    message: str
    proposed_price: Optional[float]
    status: str
    created_at: datetime
    worker: UserSchema
    repair_request: RepairRequestSchemaOut
    is_bookmarked: bool = False
    bookmark_info: Optional[BookmarkSchema] = None

    @staticmethod
    def resolve_worker(obj):
        return UserSchema.from_orm(obj.worker)

    @staticmethod
    def resolve_repair_request(obj):
        return RepairRequestSchemaOut.from_orm(obj.repair_request)

    @staticmethod
    def resolve_is_bookmarked(obj):
        # Этот метод будет реализован в сервисе
        return False

    @staticmethod
    def resolve_bookmark_info(obj):
        # Этот метод будет реализован в сервисе
        return None