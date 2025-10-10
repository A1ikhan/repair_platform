from typing import Optional

from ninja import Router, UploadedFile, File
from back.services import RepairRequestService
from back.schemas import RepairRequestSchemaIn, RepairRequestSchemaOut
from ..dependencies import customer_required

router = Router(tags=["Repairs"])

@router.get("/", response=list[RepairRequestSchemaOut], auth=None)
def list_repair_requests(request):
    """Получить все заявки на ремонт"""
    return RepairRequestService.get_all_requests()
@router.get("/search", response=list[RepairRequestSchemaOut], auth=None)
def search_repair_requests(request, search: str = None, device_type: str = None, status: str = None):
    """Поиск заявок по ключевым словам, типу устройства и статусу"""
    return RepairRequestService.search_requests(search, device_type, status)

@router.get("/filters", response=dict, auth=None)
def get_available_filters(request):
    """Получить доступные фильтры для заявок"""
    return RepairRequestService.get_available_filters()


@router.get("/{request_id}", response=RepairRequestSchemaOut, auth=None)
def get_repair_request(request, request_id: int):
    """Получить конкретную заявку по ID"""
    return RepairRequestService.get_request_by_id(request_id)

@router.get("/my/requests", response=list[RepairRequestSchemaOut])
def get_my_requests(request):
    """Получить все заявки текущего пользователя"""
    return RepairRequestService.get_user_requests(request.user)

@router.post("/", response=RepairRequestSchemaOut)
def create_repair_request(
    request,
    data: RepairRequestSchemaIn,
    file: Optional[UploadedFile] = File(None),
    file_description: Optional[str] = None
):
    """Создать новую заявку (только для клиента)"""
    customer = customer_required(request)
    return RepairRequestService.create_request(data, customer,file,file_description)

@router.put("/{request_id}", response=RepairRequestSchemaOut)
def update_repair_request(request, request_id: int, data: RepairRequestSchemaIn):
    """Обновить заявку (только автор может менять)"""
    return RepairRequestService.update_request(request_id, data, request.user)

@router.delete("/{request_id}", response=dict)
def delete_repair_request(request, request_id: int):
    """Удалить заявку (только автор может удалить)"""
    return RepairRequestService.delete_request(request_id, request.user)

@router.get("/search", response=list[RepairRequestSchemaOut], auth=None)
def search_repair_requests(request, search: str = None, device_type: str = None, status: str = None):
    """Поиск заявок по ключевым словам, типу устройства и статусу"""
    return RepairRequestService.search_requests(search, device_type, status)

@router.get("/filters", response=dict, auth=None)
def get_available_filters(request):
    """Получить доступные фильтры для заявок"""
    return RepairRequestService.get_available_filters()
