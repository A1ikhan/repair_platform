from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('new_response', 'New Response'),
            ('response_accepted', 'Response Accepted'),
            ('new_review', 'New Review'),
        ]
    )

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"
