from django.db import models
from django.utils import timezone
from ninja.errors import HttpError
from back.models.bookmark_models import Bookmark, BookmarkFolder, BookmarkHistory
from back.models.response_models import Response


class BookmarkService:
    """Сервис для работы с закладками"""

    @staticmethod
    def create_bookmark_folder(user, name: str, color: str = '#3B82F6'):
        """Создать папку для закладок"""
        folder, created = BookmarkFolder.objects.get_or_create(
            user=user,
            name=name,
            defaults={'color': color}
        )

        if not created:
            raise HttpError(400, "Folder with this name already exists")

        return folder

    @staticmethod
    def get_user_folders(user):
        """Получить все папки пользователя"""
        return BookmarkFolder.objects.filter(user=user).prefetch_related('bookmarks')

    @staticmethod
    def update_bookmark_folder(user, folder_id: int, data: dict):
        """Обновить папку закладок"""
        try:
            folder = BookmarkFolder.objects.get(id=folder_id, user=user)

            update_fields = []
            for field, value in data.items():
                if hasattr(folder, field) and value is not None:
                    setattr(folder, field, value)
                    update_fields.append(field)

            if update_fields:
                folder.save(update_fields=update_fields)

            return folder

        except BookmarkFolder.DoesNotExist:
            raise HttpError(404, "Folder not found")

    @staticmethod
    def delete_bookmark_folder(user, folder_id: int):
        """Удалить папку закладок"""
        try:
            folder = BookmarkFolder.objects.get(id=folder_id, user=user)

            # Перемещаем закладки в корень (без папки)
            Bookmark.objects.filter(folder=folder).update(folder=None)
            folder.delete()

            return {"message": "Folder deleted successfully"}

        except BookmarkFolder.DoesNotExist:
            raise HttpError(404, "Folder not found")

    @staticmethod
    def create_bookmark(user, response_id: int, data: dict):
        """Создать закладку на отклик"""
        try:
            response = Response.objects.get(id=response_id)

            # Проверяем, что пользователь - автор отклика
            if response.worker != user:
                raise HttpError(403, "You can only bookmark your own responses")

            # Проверяем, не существует ли уже закладка
            if Bookmark.objects.filter(user=user, response=response).exists():
                raise HttpError(400, "Response already bookmarked")

            bookmark_data = {
                'user': user,
                'response': response,
                'priority': data.get('priority', 'medium'),
                'planned_date': data.get('planned_date'),
                'reminder_date': data.get('reminder_date'),
                'deadline': data.get('deadline'),
                'notes': data.get('notes') or '',
                'personal_rating': data.get('personal_rating'),
            }

            # Если указана папка, проверяем принадлежность
            folder_id = data.get('folder_id')
            if folder_id:
                try:
                    folder = BookmarkFolder.objects.get(id=folder_id, user=user)
                    bookmark_data['folder'] = folder
                except BookmarkFolder.DoesNotExist:
                    raise HttpError(404, "Folder not found")

            bookmark = Bookmark.objects.create(**bookmark_data)

            # Записываем в историю
            BookmarkHistory.objects.create(
                bookmark=bookmark,
                changed_by=user,
                changes={'created': True}
            )

            return bookmark

        except Response.DoesNotExist:
            raise HttpError(404, "Response not found")

    @staticmethod
    def get_user_bookmarks(user, filters: dict = None):
        """Получить закладки пользователя с фильтрацией"""
        queryset = Bookmark.objects.filter(user=user).select_related(
            'response',
            'response__repair_request',
            'response__repair_request__created_by',
            'folder'
        )

        if filters:
            # Фильтрация по папке
            if filters.get('folder_id'):
                if filters['folder_id'] == 'none':
                    queryset = queryset.filter(folder__isnull=True)
                else:
                    queryset = queryset.filter(folder_id=filters['folder_id'])

            # Фильтрация по приоритету
            if filters.get('priority'):
                queryset = queryset.filter(priority=filters['priority'])

            # Фильтрация по статусу
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])

            # Фильтрация по дате планирования
            if filters.get('planned_date_from'):
                queryset = queryset.filter(planned_date__gte=filters['planned_date_from'])
            if filters.get('planned_date_to'):
                queryset = queryset.filter(planned_date__lte=filters['planned_date_to'])

            # Фильтрация по напоминаниям
            if filters.get('has_reminder') is not None:
                if filters['has_reminder']:
                    queryset = queryset.filter(reminder_date__isnull=False)
                else:
                    queryset = queryset.filter(reminder_date__isnull=True)

            # Фильтрация по просроченным
            if filters.get('is_overdue') is not None:
                from django.utils import timezone
                if filters['is_overdue']:
                    queryset = queryset.filter(
                        deadline__lt=timezone.now().date(),
                        status__in=['new', 'in_progress']
                    )
                else:
                    queryset = queryset.exclude(
                        deadline__lt=timezone.now().date(),
                        status__in=['new', 'in_progress']
                    )

        return queryset

    @staticmethod
    def update_bookmark(user, bookmark_id: int, data: dict):
        """Обновить закладку"""
        try:
            bookmark = Bookmark.objects.get(id=bookmark_id, user=user)

            changes = {}
            update_fields = []

            for field, value in data.items():
                if hasattr(bookmark, field) and value is not None:
                    old_value = getattr(bookmark, field)
                    setattr(bookmark, field, value)
                    update_fields.append(field)

                    # Запоминаем изменения для истории
                    if old_value != value:
                        changes[field] = [str(old_value), str(value)]

            # Обработка папки отдельно
            folder_id = data.get('folder_id')
            if folder_id is not None:
                old_folder = bookmark.folder
                if folder_id == 'none':
                    bookmark.folder = None
                else:
                    try:
                        folder = BookmarkFolder.objects.get(id=folder_id, user=user)
                        bookmark.folder = folder
                    except BookmarkFolder.DoesNotExist:
                        raise HttpError(404, "Folder not found")

                if old_folder != bookmark.folder:
                    changes['folder'] = [
                        str(old_folder.id) if old_folder else 'None',
                        str(bookmark.folder.id) if bookmark.folder else 'None'
                    ]
                update_fields.append('folder')

            if update_fields:
                bookmark.save(update_fields=update_fields)

                # Сохраняем историю изменений
                if changes:
                    BookmarkHistory.objects.create(
                        bookmark=bookmark,
                        changed_by=user,
                        changes=changes
                    )

            return bookmark

        except Bookmark.DoesNotExist:
            raise HttpError(404, "Bookmark not found")

    @staticmethod
    def delete_bookmark(user, bookmark_id: int):
        """Удалить закладку"""
        try:
            bookmark = Bookmark.objects.get(id=bookmark_id, user=user)
            bookmark.delete()
            return {"message": "Bookmark deleted successfully"}
        except Bookmark.DoesNotExist:
            raise HttpError(404, "Bookmark not found")

    @staticmethod
    def get_bookmark_stats(user):
        """Получить статистику по закладкам"""
        bookmarks = Bookmark.objects.filter(user=user)

        # Статистика по приоритетам
        priority_stats = bookmarks.values('priority').annotate(
            count=models.Count('id')
        )
        priority_dict = {item['priority']: item['count'] for item in priority_stats}

        # Статистика по статусам
        status_stats = bookmarks.values('status').annotate(
            count=models.Count('id')
        )
        status_dict = {item['status']: item['count'] for item in status_stats}

        # Просроченные закладки
        overdue_count = bookmarks.filter(
            deadline__lt=timezone.now().date(),
            status__in=['new', 'in_progress']
        ).count()

        # Закладки с напоминаниями
        with_reminder_count = bookmarks.filter(
            reminder_date__isnull=False,
            status__in=['new', 'in_progress']
        ).count()

        # Завершенные на этой неделе
        week_ago = timezone.now() - timezone.timedelta(days=7)
        completed_this_week = bookmarks.filter(
            status='completed',
            updated_at__gte=week_ago
        ).count()

        return {
            'total_bookmarks': bookmarks.count(),
            'by_priority': priority_dict,
            'by_status': status_dict,
            'overdue_count': overdue_count,
            'with_reminder_count': with_reminder_count,
            'completed_this_week': completed_this_week
        }

    @staticmethod
    def get_upcoming_bookmarks(user, days: int = 7):
        """Получить предстоящие закладки"""
        from datetime import timedelta
        today = timezone.now().date()
        future_date = today + timedelta(days=days)

        return Bookmark.objects.filter(
            user=user,
            planned_date__gte=today,
            planned_date__lte=future_date,
            status__in=['new', 'in_progress']
        ).select_related(
            'response',
            'response__repair_request',
            'folder'
        ).order_by('planned_date', 'priority')

    @staticmethod
    def enrich_responses_with_bookmarks(user, responses):
        """Обогатить ответы информацией о закладках"""
        response_ids = [response.id for response in responses]

        # Получаем все закладки пользователя для этих откликов
        bookmarks = {
            b.response_id: b
            for b in Bookmark.objects.filter(
                user=user,
                response_id__in=response_ids
            ).select_related('folder')
        }

        for response in responses:
            bookmark = bookmarks.get(response.id)
            response._bookmark = bookmark

        return list(responses)


class BookmarkNotificationService:
    """Сервис уведомлений для закладок"""

    @staticmethod
    def check_reminders():
        """Проверить напоминания и отправить уведомления"""
        from back.services.notification_service import NotificationService

        now = timezone.now()
        upcoming_reminders = Bookmark.objects.filter(
            reminder_date__lte=now + timezone.timedelta(hours=1),
            reminder_date__gte=now,
            status__in=['new', 'in_progress']
        ).select_related('user', 'response', 'response__repair_request')

        for bookmark in upcoming_reminders:
            message = f"Напоминание: {bookmark.response.repair_request.title} - планируется на {bookmark.planned_date}"
            NotificationService.create_notification(
                bookmark.user,
                message,
                'bookmark_reminder'
            )

    @staticmethod
    def check_overdue():
        """Проверить просроченные закладки"""
        from back.services.notification_service import NotificationService

        today = timezone.now().date()
        overdue_bookmarks = Bookmark.objects.filter(
            deadline__lt=today,
            status__in=['new', 'in_progress']
        ).select_related('user', 'response', 'response__repair_request')

        for bookmark in overdue_bookmarks:
            message = f"Просрочено: {bookmark.response.repair_request.title} - крайний срок был {bookmark.deadline}"
            NotificationService.create_notification(
                bookmark.user,
                message,
                'bookmark_overdue'
            )