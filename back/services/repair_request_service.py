from ninja.errors import HttpError
from back.models import RepairRequest
from django.db import models


class RepairRequestService:
    @staticmethod
    def get_all_requests():
        return RepairRequest.objects.select_related('created_by').all()

    @staticmethod
    def get_request_by_id(request_id: int):
        try:
            return RepairRequest.objects.select_related('created_by').get(id=request_id)
        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def get_user_requests(user):
        return RepairRequest.objects.filter(created_by=user).select_related('created_by')

    @staticmethod
    def create_request(data, user):
        return RepairRequest.objects.create(
            **data.dict(),
            created_by=user,
            status='new'
        )

    @staticmethod
    def update_request(request_id: int, data, user):
        try:
            repair_request = RepairRequest.objects.get(id=request_id, created_by=user)
            for attr, value in data.dict().items():
                setattr(repair_request, attr, value)
            repair_request.save()
            return repair_request
        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found or you don't have permission")

    @staticmethod
    def delete_request(request_id: int, user):
        try:
            repair_request = RepairRequest.objects.get(id=request_id, created_by=user)
            repair_request.delete()
            return {"message": "Repair request deleted successfully"}
        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found or you don't have permission")

    @staticmethod
    def search_requests(search_term: str = None, device_type: str = None, status: str = None):
        queryset = RepairRequest.objects.select_related('created_by')

        if search_term:
            queryset = queryset.filter(
                models.Q(title__icontains=search_term) |
                models.Q(description__icontains=search_term)
            )
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    @staticmethod
    def get_available_filters():
        return {
            'device_types': [choice[0] for choice in RepairRequest.DEVICE_TYPES],
            'statuses': [choice[0] for choice in RepairRequest.STATUS_CHOICES]
        }
