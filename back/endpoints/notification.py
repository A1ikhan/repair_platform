from ninja import Router
from back.services import NotificationService

router = Router(tags=["Notifications"])

@router.get("/", response=list[dict])
def get_notifications(request):
    notifications = NotificationService.get_user_notifications(request.user)
    return [{
        'id': n.id,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at,
        'type': n.notification_type
    } for n in notifications]

@router.post("/{notification_id}/read", response=dict)
def mark_notification_read(request, notification_id: int):
    NotificationService.mark_as_read(notification_id, request.user)
    return {"message": "Notification marked as read"}
