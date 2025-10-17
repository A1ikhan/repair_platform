from django.db import models
from django.contrib.auth.models import User


class UserLocation(models.Model):
    """Модель для хранения местоположения пользователей"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='location')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.TextField(blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['city']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.address}"


class ServiceArea(models.Model):
    """Зоны обслуживания для работников"""
    worker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_areas')
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    radius_km = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.worker.username} - {self.city} ({self.radius_km}km)"