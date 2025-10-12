# back/models/response_models.py
from django.db import models
from django.contrib.auth.models import User
from .repair_requests_models import RepairRequest


class Response(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    repair_request = models.ForeignKey(
        RepairRequest,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    worker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    message = models.TextField()
    proposed_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='sent'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['repair_request', 'worker']  # один работник - один отклик на заявку

    def __str__(self):
        return f"Response from {self.worker.username} for request #{self.repair_request.id}"