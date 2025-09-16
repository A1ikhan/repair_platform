from django.db import models
from django.contrib.auth.models import User

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
    experience = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0.0)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Worker: {self.user.username}"

    @property
    def user_type(self):
        return 'worker'
