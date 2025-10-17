from ninja.errors import HttpError
from back.models import RepairRequest
from .notification_service import NotificationService
from back import models

from .userlist_service import AutoListService


class ResponseService:
    @staticmethod
    def create_response(repair_request_id: int, data, worker):
        try:
            repair_request = RepairRequest.objects.get(id=repair_request_id)
            if models.Response.objects.filter(repair_request=repair_request, worker=worker).exists():
                raise HttpError(400, "You have already responded to this request")

            response = models.Response.objects.create(
                repair_request=repair_request,
                worker=worker,
                message=data.message,
                proposed_price=data.proposed_price,
                status='sent'
            )

            NotificationService.notify_new_response(repair_request, response)
            AutoListService.handle_response_created(response)
            return response

        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def get_responses_for_request(repair_request_id: int, user):
        try:
            repair_request = RepairRequest.objects.get(id=repair_request_id)
            if repair_request.created_by != user and not models.Response.objects.filter(
                repair_request=repair_request, worker=user
            ).exists():
                raise HttpError(403, "Access denied")

            return models.Response.objects.filter(repair_request=repair_request).select_related('worker')
        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def get_worker_responses(worker):
        return models.Response.objects.filter(worker=worker).select_related('repair_request')

    @staticmethod
    def accept_response(response_id: int, customer):
        try:
            response = models.Response.objects.get(id=response_id)
            if response.repair_request.created_by != customer:
                raise HttpError(403, "Only the request owner can accept responses")

            response.status = 'accepted'
            response.save()
            response.repair_request.status = 'active'
            response.repair_request.save()

            models.Response.objects.filter(
                repair_request=response.repair_request
            ).exclude(id=response_id).update(status='rejected')

            NotificationService.notify_response_accepted(response)
            AutoListService.handle_response_accepted(response)
            return response

        except models.Response.DoesNotExist:
            raise HttpError(404, "Response not found")
