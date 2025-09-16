from django.db import models
from django.contrib.auth.models import User



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
