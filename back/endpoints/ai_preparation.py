from ninja import Router, File, UploadedFile
from typing import List
from back.schemas import (
    Message, ProblemPhotoSchema, ProblemPhotoUploadSchema,
    PricePredictionSchema, FinalPriceUpdateSchema, RepairRequestSchemaOut
)
from back.services.repair_request_service import (RepairRequestService, SimplePriceEstimator,
                                                  DataCollectionService)

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
    """Предварительная оценка цены ремонта"""
    return SimplePriceEstimator.estimate_price(device_type, description)

@router.get("/data-stats", response=dict, auth=None)
def get_data_collection_stats(request):
    """Статистика собранных данных для ИИ"""
    return DataCollectionService.get_training_data_stats()

@router.get("/repairs/{repair_request_id}/analysis", response=dict, auth=None)
def get_problem_analysis(request, repair_request_id: int):
    """Анализ проблемы (ключевые слова и сложность)"""
    return RepairRequestService.get_problem_analysis(repair_request_id)