from django.db import models
from django.contrib.auth.models import User
from back.models.repair_requests_models import RepairRequest


class Review(models.Model):
    repair_request = models.OneToOneField(RepairRequest, on_delete=models.CASCADE, related_name='review')
    worker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['repair_request', 'customer']

    def __str__(self):
        return f"Review for {self.worker.username} - {self.rating} stars"
