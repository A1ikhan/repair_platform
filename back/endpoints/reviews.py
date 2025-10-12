from ninja import Router
from back.schemas import ReviewSchemaOut, ReviewSchemaIn
from back.services import ReviewService
from ..dependencies import customer_required

router = Router(tags=["Reviews"])

@router.post("/request/{repair_request_id}", response=ReviewSchemaOut)
def create_review(request, repair_request_id: int, data: ReviewSchemaIn):
    customer = customer_required(request)
    return ReviewService.create_review(repair_request_id, data, customer)

@router.get("/worker/{worker_id}", response=list[ReviewSchemaOut])
def get_worker_reviews(request, worker_id: int):
    return ReviewService.get_worker_reviews(worker_id)

@router.get("/my", response=list[ReviewSchemaOut])
def get_my_reviews(request):
    """Получить все отзывы, оставленные текущим пользователем"""
    customer = customer_required(request)
    return ReviewService.get_my_reviews(customer)

@router.put("/{review_id}", response=ReviewSchemaOut)
def update_review(request, review_id: int, data: ReviewSchemaIn):
    """Обновить отзыв (только автор)"""
    customer = customer_required(request)
    return ReviewService.update_review(review_id, data, customer)

@router.delete("/{review_id}", response=dict)
def delete_review(request, review_id: int):
    """Удалить отзыв (только автор)"""
    customer = customer_required(request)
    return ReviewService.delete_review(review_id, customer)