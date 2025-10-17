from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill


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
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    desired_completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repair_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class RepairRequestFile(models.Model):
    repair_request = models.ForeignKey(
        'RepairRequest',
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(upload_to='repair_requests/%Y/%m/%d/')
    thumbnail = ImageSpecField(
        source='file',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 80}
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return f"File for request #{self.repair_request.id}"