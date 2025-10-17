from django.db import models
from django.contrib.auth.models import User
import os
from uuid import uuid4

from django.utils import timezone


def avatar_upload_path(instance, filename):
    """Генерация пути для загрузки аватаров"""
    ext = filename.split('.')[-1]
    filename = f"{uuid4()}.{ext}"
    return os.path.join('avatars', filename)


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)
    bio = models.TextField(blank=True, verbose_name='О себе')

    # Настройки приватности
    show_my_requests = models.BooleanField(default=True, verbose_name='Показывать мои заявки')
    show_my_responses = models.BooleanField(default=True, verbose_name='Показывать мои отклики')
    show_my_reviews = models.BooleanField(default=True, verbose_name='Показывать мои отзывы')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer: {self.user.username}"

    @property
    def user_type(self):
        return 'customer'


class WorkerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker_profile')
    phone_number = models.CharField(max_length=20, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    experience = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0.0)
    is_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)
    bio = models.TextField(blank=True, verbose_name='О себе')

    # Настройки приватности
    show_my_responses = models.BooleanField(default=True, verbose_name='Показывать мои отклики')
    show_my_reviews = models.BooleanField(default=True, verbose_name='Показывать мои отзывы')
    show_my_rating = models.BooleanField(default=True, verbose_name='Показывать мой рейтинг')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Worker: {self.user.username}"

    @property
    def user_type(self):
        return 'worker'


class UserActivity(models.Model):
    """Модель для истории действий пользователя"""

    ACTIVITY_TYPE_CHOICES = [
        ('login', 'Вход в систему'),
        ('logout', 'Выход из системы'),
        ('register', 'Регистрация'),
        ('profile_update', 'Обновление профиля'),
        ('password_change', 'Смена пароля'),
        ('avatar_update', 'Обновление аватара'),
        ('request_create', 'Создание заявки'),
        ('request_update', 'Обновление заявки'),
        ('request_delete', 'Удаление заявки'),
        ('response_create', 'Создание отклика'),
        ('response_accept', 'Принятие отклика'),
        ('review_create', 'Создание отзыва'),
        ('favorite_add', 'Добавление в избранное'),
        ('favorite_remove', 'Удаление из избранного'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPE_CHOICES)
    description = models.TextField(blank=True)

    # Ссылка на связанный объект (если есть)
    target_model = models.CharField(max_length=100, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User activities'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.created_at}"