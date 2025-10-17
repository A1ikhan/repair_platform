from ninja import Router
from typing import List, Optional
from back.schemas import (
    LocationSchema, LocationUpdateSchema, NearbyWorkersResponse,
    PartsShopSchema, GeocodeResponse, LocationResponse, Message
)
from back.services.geolocation_service import LocationService
from back.dependencies import customer_required, worker_required

router = Router(tags=["Geolocation"])


@router.post("/location/update", response=GeocodeResponse, auth=None)
def update_my_location(request, data: LocationUpdateSchema):
    """Обновить местоположение пользователя"""
    return LocationService.update_user_location(request.user, data.address)


@router.get("/location/me", response=LocationResponse, auth=None)
def get_my_location(request):
    """Получить мое местоположение"""
    return LocationService.get_user_location(request.user)


@router.get("/workers/nearby", response=List[NearbyWorkersResponse], auth=None)
def get_nearby_workers(request, address: str, max_distance: int = 10):
    """Найти работников поблизости"""
    from back.services.geolocation_service import DGisService

    dgis = DGisService()
    geocode_result = dgis.geocode_address(address)

    if not geocode_result:
        return []

    return LocationService.find_nearby_workers(
        geocode_result['latitude'],
        geocode_result['longitude'],
        max_distance
    )


@router.get("/shops/parts/nearby", response=List[PartsShopSchema], auth=None)
def get_nearby_parts_shops(request, lat: float, lon: float, part_name: Optional[str] = None):
    """Найти магазины запчастей поблизости"""
    return LocationService.search_nearby_parts_shops(lat, lon, part_name)


@router.post("/workers/{worker_id}/service-area", response=Message, auth=None)
def add_service_area(request, worker_id: int, city: str, radius_km: int = 10):
    """Добавить зону обслуживания для работника"""
    from back.models.geolocation_models import ServiceArea
    from django.contrib.auth.models import User

    worker = User.objects.get(id=worker_id)
    if worker != request.user and not request.user.is_staff:
        return 403, {"message": "Permission denied"}

    ServiceArea.objects.create(
        worker=worker,
        city=city,
        radius_km=radius_km
    )

    return {"message": "Service area added successfully"}


@router.delete("/location/me", response=Message, auth=None)
def delete_my_location(request):
    """Удалить мою локацию"""
    from back.models.geolocation_models import UserLocation

    try:
        user_location = UserLocation.objects.get(user=request.user)
        user_location.delete()
        return {"message": "Location deleted successfully"}
    except UserLocation.DoesNotExist:
        return {"message": "Location not found"}