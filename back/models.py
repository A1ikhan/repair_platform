from django.db import models

# Create your models here.
# back/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Customer: {self.user.username}"

    @property
    def user_type(self):
        return 'customer'
class WorkerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker_profile')
    phone_number = models.CharField(max_length=20, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    experience = models.PositiveIntegerField(default=0)  # Опыт в годах
    rating = models.FloatField(default=0.0)
    is_verified = models.BooleanField(default=False)  # Подтвержден ли админом

    def __str__(self):
        return f"Worker: {self.user.username}"
    @property
    def user_type(self):
        return 'worker'

class RepairRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('active', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    DEVICE_TYPES = [
        ('fridge', 'Refrigerator'),
        ('washer', 'Washing Machine'),
        ('oven', 'Oven'),
        ('dishwasher', 'Dishwasher'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPES)
    address = models.TextField()
    desired_completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repair_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Сигналы для автоматического создания профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'customer_profile') and not hasattr(instance, 'worker_profile'):
        # Пока просто создаем пустой профиль. Логику выбора типа пользователя добавим позже.
        CustomerProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'customer_profile'):
        instance.customer_profile.save()
    # Пока не создаем WorkerProfile автоматически. Он будет создаваться по запросу.