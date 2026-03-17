from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from back.models.response_models import Response


class BookmarkFolder(models.Model):
    """Папка для организации закладок"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmark_folders')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#3B82F6')  # HEX цвет
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        unique_together = ['user', 'name']  # Уникальное имя папки для пользователя

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class Bookmark(models.Model):
    """Закладка на отклик"""
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('urgent', 'Срочный'),
    ]

    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='bookmarks')
    folder = models.ForeignKey(BookmarkFolder, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='bookmarks')

    # Поля планирования
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    planned_date = models.DateField(null=True, blank=True)  # Планируемая дата выполнения
    reminder_date = models.DateTimeField(null=True, blank=True)  # Напоминание
    deadline = models.DateField(null=True, blank=True)  # Крайний срок

    # Персональные заметки
    notes = models.TextField(blank=True)
    personal_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])  # 1-5 звезд

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'planned_date', '-created_at']
        unique_together = ['user', 'response']  # Один отклик - одна закладка у пользователя
        indexes = [
            models.Index(fields=['user', 'priority']),
            models.Index(fields=['user', 'planned_date']),
            models.Index(fields=['user', 'status']),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(personal_rating__gte=1) & models.Q(personal_rating__lte=5)
                    | models.Q(personal_rating__isnull=True)
                ),
                name='bookmark_personal_rating_1_to_5',
            ),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.response.repair_request.title}"

    @property
    def is_overdue(self):
        """Просрочена ли закладка"""
        from django.utils import timezone
        if self.deadline and self.status != 'completed':
            return self.deadline < timezone.now().date()
        return False

    @property
    def has_reminder(self):
        """Есть ли активное напоминание"""
        from django.utils import timezone
        if self.reminder_date and self.status != 'completed':
            return self.reminder_date > timezone.now()
        return False


class BookmarkHistory(models.Model):
    """История изменений закладки"""
    bookmark = models.ForeignKey(Bookmark, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    changes = models.JSONField()  # {field: [old_value, new_value]}
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"History for {self.bookmark} at {self.created_at}"