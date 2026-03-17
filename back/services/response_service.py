import logging
from django.db import transaction
from ninja.errors import HttpError
from back.models import RepairRequest, Response
from .bookmark_service import BookmarkService
from .notification_service import NotificationService
from back import models

from .userlist_service import AutoListService

logger = logging.getLogger(__name__)


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

            logger.info("Worker %s submitted response #%s to request #%s", worker.id, response.id, repair_request_id)
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
        """Получить отклики работника с информацией о закладках"""
        responses = Response.objects.filter(worker=worker).select_related(
            'repair_request',
            'repair_request__created_by'
        ).order_by('-created_at')

        # Обогащаем информацией о закладках
        return BookmarkService.enrich_responses_with_bookmarks(worker, responses)

    @staticmethod
    def get_response_with_bookmarks(response_id: int, user):
        """Получить отклик с информацией о закладках"""
        try:
            response = Response.objects.select_related(
                'repair_request',
                'repair_request__created_by'
            ).get(id=response_id)

            # Обогащаем информацией о закладках
            enriched = BookmarkService.enrich_responses_with_bookmarks(user, [response])
            return enriched[0] if enriched else None

        except Response.DoesNotExist:
            raise HttpError(404, "Response not found")
        
    @staticmethod
    def accept_response(response_id: int, customer):
        try:
            response = models.Response.objects.select_related('repair_request').get(id=response_id)
            if response.repair_request.created_by != customer:
                raise HttpError(403, "Only the request owner can accept responses")

            with transaction.atomic():
                response.status = 'accepted'
                response.save()
                response.repair_request.status = 'active'
                response.repair_request.save()
                models.Response.objects.filter(
                    repair_request=response.repair_request
                ).exclude(id=response_id).update(status='rejected')

            logger.info("Customer %s accepted response #%s for request #%s", customer.id, response_id, response.repair_request_id)
            NotificationService.notify_response_accepted(response)
            AutoListService.handle_response_accepted(response)
            return response

        except models.Response.DoesNotExist:
            raise HttpError(404, "Response not found")
