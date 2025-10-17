from ninja.errors import HttpError
from back.models import RepairRequest
from django.db import models

from back.models.repair_requests_models import RepairRequestFile

from back.models import Response
from back.services.userlist_service import AutoListService


class RepairRequestService:
    @staticmethod
    def get_all_requests():
        return RepairRequest.objects.select_related('created_by').prefetch_related('files').all()

    @staticmethod
    def get_request_by_id(request_id: int):
        try:
            return RepairRequest.objects.select_related('created_by').prefetch_related('files').get(id=request_id)
        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def get_user_requests(user):
        return RepairRequest.objects.filter(created_by=user).select_related('created_by').prefetch_related('files')


    @staticmethod
    def create_request(data, user, files: list = None, file_descriptions: list = None, is_public: bool = True):
        # Создаем саму заявку
        repair_request = RepairRequest.objects.create(
            **data.dict(),
            created_by=user,
            status='new'
        )

        if files:
            for i, file in enumerate(files):
                RepairRequestFile.objects.create(
                    repair_request=repair_request,
                    file=file,
                    uploaded_by=user,
                    description=(file_descriptions[i] if file_descriptions and i < len(file_descriptions) else ''),
                    is_public=is_public
                )

        return repair_request
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
    def complete_request(request_id: int, user):
        """Завершить заявку (только автор или принятый работник)"""
        try:
            repair_request = RepairRequest.objects.get(id=request_id)

            # Проверяем права
            can_complete = (
                    user == repair_request.created_by or
                    Response.objects.filter(
                        repair_request=repair_request,
                        worker=user,
                        status='accepted'
                    ).exists()
            )

            if not can_complete:
                raise HttpError(403, "No permission to complete this request")

            repair_request.status = 'completed'
            repair_request.save()

            # Автоматически управляем списками
            AutoListService.handle_request_completed(repair_request)

            return repair_request
        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

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
