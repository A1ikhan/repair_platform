from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill

class ProblemPhoto(models.Model):
    """Модель для фото проблем"""
    image = models.ImageField(upload_to='problem_photos/%Y/%m/%d/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Photo by {self.uploaded_by.username}"

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

    predicted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_confidence = models.FloatField(default=0.0)  # Уверенность предсказания 0-1
    ai_analysis_data = models.JSONField(default=dict, blank=True)  # Данные анализа ИИ

    # Связь с фото
    problem_photos = models.ManyToManyField(ProblemPhoto, blank=True)

    # Финальная цена после ремонта
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.title


class PriceHistory(models.Model):
    """История цен для обучения ИИ"""
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.CASCADE, related_name='price_history')
    device_type = models.CharField(max_length=50)
    problem_description = models.TextField()
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['device_type', 'final_price']),
        ]
        verbose_name_plural = 'Price histories'

    def __str__(self):
        return f"Price history for {self.repair_request.title}"



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