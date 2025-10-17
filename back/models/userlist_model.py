from django.db import models
from django.contrib.auth.models import User
from back.models.repair_requests_models import RepairRequest


class UserList(models.Model):
    """Модель пользовательского списка (Избранное, Смотрю и т.д.)"""
    LIST_TYPES = [
        ('favorite', 'Избранное'),
        ('watching', 'Смотрю'),
        ('applied', 'Подался'),
        ('completed', 'Выполнено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_lists')
    name = models.CharField(max_length=50, choices=LIST_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'name']
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_name_display()}"


class ListItem(models.Model):
    """Элемент в пользовательском списке"""
    user_list = models.ForeignKey(UserList, on_delete=models.CASCADE, related_name='items')
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.CASCADE, related_name='list_items')
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)  # Персональные заметки пользователя

    class Meta:
        unique_together = ['user_list', 'repair_request']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.repair_request.title} in {self.user_list.name}"