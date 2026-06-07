from ninja import Router, File, UploadedFile
from typing import List, Optional
from back.schemas import (
    Message, ProblemPhotoSchema, ProblemPhotoUploadSchema,
    PricePredictionSchema, FinalPriceUpdateSchema, RepairRequestSchemaOut
)
from back.services.repair_request_service import (RepairRequestService, SimplePriceEstimator,
                                                  DataCollectionService)
from back.services.price_estimation_service import PriceEstimationService

router = Router(tags=["AI Preparation"])

@router.post("/repairs/{repair_request_id}/photos", response=ProblemPhotoSchema, auth=None)
def add_problem_photo(
    request,
    repair_request_id: int,
    description: str = None,
    file: UploadedFile = File(...)
):
    """Добавить фото проблемы к заявке"""
    return RepairRequestService.add_problem_photo(
        repair_request_id, file, description, request.user
    )

@router.get("/repairs/{repair_request_id}/photos", response=List[ProblemPhotoSchema], auth=None)
def get_problem_photos(request, repair_request_id: int):
    """Получить фото проблемы заявки"""
    repair_request = RepairRequestService.get_request_by_id(repair_request_id)
    return list(repair_request.problem_photos.all())

@router.post("/repairs/{repair_request_id}/final-price", response=RepairRequestSchemaOut, auth=None)
def update_final_price(request, repair_request_id: int, data: FinalPriceUpdateSchema):
    """Обновить финальную цену после ремонта"""
    return RepairRequestService.update_final_price(
        repair_request_id, data.final_price, request.user
    )

@router.post("/estimate-price", response=PricePredictionSchema, auth=None)
def estimate_repair_price(request, device_type: str, description: str):
    """Оценка цены по описанию (ключевые слова + правила)"""
    return PriceEstimationService.estimate(device_type, description)


@router.post("/estimate-price-with-photo", response=PricePredictionSchema, auth=None)
def estimate_repair_price_with_photo(
    request,
    device_type: str,
    description: str,
    file: Optional[UploadedFile] = File(None),
):
    """
    Оценка цены по описанию + фото.
    Фото анализируется через Claude Vision API (если задан ANTHROPIC_API_KEY).
    Без API-ключа работает как обычная оценка по ключевым словам.
    """
    image_bytes = None
    media_type = "image/jpeg"

    if file:
        image_bytes = file.read()
        media_type = file.content_type or "image/jpeg"

    return PriceEstimationService.estimate(device_type, description, image_bytes, media_type)

@router.get("/data-stats", response=dict, auth=None)
def get_data_collection_stats(request):
    """Статистика собранных данных для ИИ"""
    return DataCollectionService.get_training_data_stats()

@router.get("/repairs/{repair_request_id}/analysis", response=dict, auth=None)
def get_problem_analysis(request, repair_request_id: int):
    """Анализ проблемы (ключевые слова и сложность)"""
    return RepairRequestService.get_problem_analysis(repair_request_id)