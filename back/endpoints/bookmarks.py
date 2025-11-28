from ninja import Router
from typing import List, Optional
from back.schemas import (
    BookmarkFolderSchema, BookmarkFolderCreate, BookmarkFolderUpdate,
    BookmarkSchema, BookmarkCreate, BookmarkUpdate,
    BookmarkStatsSchema, BookmarkFilterSchema, Message
)
from back.services.bookmark_service import BookmarkService
from back.dependencies import worker_required

router = Router(tags=["Bookmarks"])


# Папки закладок
@router.post("/folders", response=BookmarkFolderSchema)
def create_bookmark_folder(request, data: BookmarkFolderCreate):
    """Создать папку для закладок"""
    worker = worker_required(request)
    return BookmarkService.create_bookmark_folder(worker, data.name, data.color)


@router.get("/folders", response=List[BookmarkFolderSchema])
def get_my_folders(request):
    """Получить мои папки закладок"""
    worker = worker_required(request)
    return BookmarkService.get_user_folders(worker)


@router.put("/folders/{folder_id}", response=BookmarkFolderSchema)
def update_bookmark_folder(request, folder_id: int, data: BookmarkFolderUpdate):
    """Обновить папку закладок"""
    worker = worker_required(request)
    return BookmarkService.update_bookmark_folder(worker, folder_id, data.dict(exclude_unset=True))


@router.delete("/folders/{folder_id}", response=Message)
def delete_bookmark_folder(request, folder_id: int):
    """Удалить папку закладок"""
    worker = worker_required(request)
    return BookmarkService.delete_bookmark_folder(worker, folder_id)


# Закладки
@router.post("/bookmarks", response=BookmarkSchema)
def create_bookmark(request, data: BookmarkCreate):
    """Создать закладку на отклик"""
    worker = worker_required(request)
    return BookmarkService.create_bookmark(worker, data.repair_request_id, data.dict(exclude_unset=True))


@router.get("/bookmarks", response=List[BookmarkSchema])
def get_my_bookmarks(
        request,
        folder_id: Optional[int] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        planned_date_from: Optional[str] = None,
        planned_date_to: Optional[str] = None,
        has_reminder: Optional[bool] = None,
        is_overdue: Optional[bool] = None
):
    """Получить мои закладки с фильтрацией"""
    worker = worker_required(request)

    filters = {}
    if folder_id is not None:
        filters['folder_id'] = folder_id
    if priority:
        filters['priority'] = priority
    if status:
        filters['status'] = status
    if planned_date_from:
        filters['planned_date_from'] = planned_date_from
    if planned_date_to:
        filters['planned_date_to'] = planned_date_to
    if has_reminder is not None:
        filters['has_reminder'] = has_reminder
    if is_overdue is not None:
        filters['is_overdue'] = is_overdue

    return BookmarkService.get_user_bookmarks(worker, filters)


@router.get("/bookmarks/upcoming", response=List[BookmarkSchema])
def get_upcoming_bookmarks(request, days: int = 7):
    """Получить предстоящие закладки"""
    worker = worker_required(request)
    return BookmarkService.get_upcoming_bookmarks(worker, days)


@router.put("/bookmarks/{bookmark_id}", response=BookmarkSchema)
def update_bookmark(request, bookmark_id: int, data: BookmarkUpdate):
    """Обновить закладку"""
    worker = worker_required(request)
    return BookmarkService.update_bookmark(worker, bookmark_id, data.dict(exclude_unset=True))


@router.delete("/bookmarks/{bookmark_id}", response=Message)
def delete_bookmark(request, bookmark_id: int):
    """Удалить закладку"""
    worker = worker_required(request)
    return BookmarkService.delete_bookmark(worker, bookmark_id)


@router.get("/bookmarks/stats", response=BookmarkStatsSchema)
def get_bookmark_stats(request):
    """Получить статистику по закладкам"""
    worker = worker_required(request)
    return BookmarkService.get_bookmark_stats(worker)