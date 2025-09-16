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
