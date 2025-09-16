from ninja.errors import HttpError
from back.models import Notification


class NotificationService:
    @staticmethod
    def create_notification(user, message, notification_type):
        return Notification.objects.create(
            user=user,
            message=message,
            notification_type=notification_type
        )

    @staticmethod
    def notify_new_response(repair_request, response):
        message = f"Новый отклик на вашу заявку '{repair_request.title}'"
        NotificationService.create_notification(
            repair_request.created_by,
            message,
            'new_response'
        )

    @staticmethod
    def notify_response_accepted(response):
        message = f"Ваш отклик на заявку '{response.repair_request.title}' принят!"
        NotificationService.create_notification(
            response.worker,
            message,
            'response_accepted'
        )

    @staticmethod
    def get_user_notifications(user):
        return Notification.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def mark_as_read(notification_id, user):
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.is_read = True
            notification.save()
            return notification
        except Notification.DoesNotExist:
            raise HttpError(404, "Notification not found")
