from typing import Optional, List

from ninja import Router, UploadedFile, File, Form
from ninja.pagination import paginate, PageNumberPagination
from back.services import RepairRequestService
from back.schemas import RepairRequestSchemaIn, RepairRequestSchemaOut
from ..dependencies import customer_required

router = Router(tags=["Repairs"])


@router.get("/", response=list[RepairRequestSchemaOut], auth=None)
@paginate(PageNumberPagination)
def list_repair_requests(request, **kwargs):
    """Получить все заявки на ремонт"""
    return RepairRequestService.get_all_requests()


@router.get("/search", response=list[RepairRequestSchemaOut], auth=None)
@paginate(PageNumberPagination)
def search_repair_requests(request, search: str = None, device_type: str = None, status: str = None, **kwargs):
    """Поиск заявок по ключевым словам, типу устройства и статусу"""
    return RepairRequestService.search_requests(search, device_type, status)


@router.get("/filters", response=dict, auth=None)
def get_available_filters(request):
    """Получить доступные фильтры для заявок"""
    return RepairRequestService.get_available_filters()


# /my/requests must be defined before /{request_id} to avoid 'my' being captured as an int
@router.get("/my/requests", response=list[RepairRequestSchemaOut])
def get_my_requests(request):
    """Получить все заявки текущего пользователя"""
    return RepairRequestService.get_user_requests(request.user)


@router.get("/{request_id}", response=RepairRequestSchemaOut, auth=None)
def get_repair_request(request, request_id: int):
    """Получить конкретную заявку по ID"""
    return RepairRequestService.get_request_by_id(request_id)


@router.post("/", response=RepairRequestSchemaOut)
def create_repair_request(
    request,
    data: RepairRequestSchemaIn,
    files: Optional[List[UploadedFile]] = File(None),
    descriptions: Optional[List[str]] = Form(None),
    is_public: bool = Form(True)
):
    """Создать новую заявку (только для клиента)"""
    customer = customer_required(request)
    return RepairRequestService.create_request(
        data=data,
        user=customer,
        files=files,
        file_descriptions=descriptions,
        is_public=is_public
    )


@router.put("/{request_id}", response=RepairRequestSchemaOut)
def update_repair_request(request, request_id: int, data: RepairRequestSchemaIn):
    """Обновить заявку (только автор может менять)"""
    return RepairRequestService.update_request(request_id, data, request.user)


@router.delete("/{request_id}", response=dict)
def delete_repair_request(request, request_id: int):
    """Удалить заявку (только автор может удалить)"""
    return RepairRequestService.delete_request(request_id, request.user)
