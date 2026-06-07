from django.core.cache import cache
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate, PageNumberPagination
from typing import Optional, List
from django.contrib.auth.models import User
from back.models import WorkerProfile
from back.schemas import UserSchema, UserDetailSchema
from back.schemas.base_schema import Message
from back.schemas.geolocation_schema import NearbyWorkersResponse
from back.services import WorkerService
from back.dependencies import customer_required

router = Router(tags=["Workers"])

_TOP_WORKERS_CACHE_KEY = "top_workers_ids"
_CACHE_TTL = 5 * 60  # 5 minutes


@router.get("/", response=list[UserDetailSchema], auth=None)
@paginate(PageNumberPagination)
def list_workers(
    request,
    specialization: Optional[str] = None,
    is_verified: Optional[bool] = None,
    search: Optional[str] = None,
    **kwargs,
):
    return WorkerService.list_workers(specialization=specialization, is_verified=is_verified, search=search)


@router.get("/saved", response=list[UserDetailSchema])
@paginate(PageNumberPagination)
def get_saved_workers(request, **kwargs):
    customer = customer_required(request)
    return WorkerService.get_saved_workers(customer)


@router.get("/top", response=list[UserSchema], auth=None)
def get_top_workers(request):
    worker_ids = cache.get(_TOP_WORKERS_CACHE_KEY)
    if worker_ids is None:
        worker_ids = list(
            WorkerProfile.objects.filter(is_verified=True)
            .order_by('-rating')
            .values_list('user_id', flat=True)[:10]
        )
        cache.set(_TOP_WORKERS_CACHE_KEY, worker_ids, _CACHE_TTL)

    return User.objects.filter(id__in=worker_ids).select_related(
        'worker_profile', 'customer_profile'
    )


@router.get("/{worker_id}", response=UserDetailSchema, auth=None)
def get_worker(request, worker_id: int):
    return WorkerService.get_worker_by_id(worker_id)


@router.post("/{worker_id}/save", response=Message)
def save_worker(request, worker_id: int):
    customer = customer_required(request)
    WorkerService.save_worker(customer, worker_id)
    return Message(message="Worker saved successfully")


@router.delete("/{worker_id}/save", response=Message)
def unsave_worker(request, worker_id: int):
    customer = customer_required(request)
    WorkerService.unsave_worker(customer, worker_id)
    return Message(message="Worker removed from saved")


@router.get("/ranked", response=List[NearbyWorkersResponse], auth=None)
def get_ranked_workers(
    request,
    address: str,
    device_type: Optional[str] = None,
    max_distance: int = 10,
):
    """
    Список мастеров поблизости, отранжированных по составному скору:
    рейтинг (35%) + расстояние (30%) + опыт (15%) + специализация (10%)
    + доступность (5%) + верификация (5%).

    Параметры:
    - address: адрес клиента для геокодирования
    - device_type: тип устройства (fridge, washer, oven и др.) — повышает
      скор мастеров с подходящей специализацией
    - max_distance: максимальный радиус поиска в км (по умолчанию 10)
    """
    from back.services.geolocation_service import DGisService, LocationService

    dgis = DGisService()
    geocode_result = dgis.geocode_address(address)
    if not geocode_result:
        raise HttpError(400, "Could not geocode address")

    return LocationService.find_nearby_workers(
        geocode_result['latitude'],
        geocode_result['longitude'],
        max_distance,
        device_type=device_type,
    )
