from ninja import Router
from back.schemas import ResponseSchemaIn, ResponseSchemaOut
from back.services import ResponseService
from ..dependencies import worker_required, customer_required

router = Router(tags=["Responses"])

@router.post("/request/{repair_request_id}", response=ResponseSchemaOut)
def create_response(request, repair_request_id: int, data: ResponseSchemaIn):
    worker = worker_required(request)
    return ResponseService.create_response(repair_request_id, data, worker)

@router.get("/request/{repair_request_id}", response=list[ResponseSchemaOut])
def get_responses_for_request(request, repair_request_id: int):
    return ResponseService.get_responses_for_request(repair_request_id, request.user)

@router.get("/my", response=list[ResponseSchemaOut])
def get_my_responses(request):
    worker = worker_required(request)
    return ResponseService.get_worker_responses(worker)

@router.post("/{response_id}/accept", response=ResponseSchemaOut)
def accept_response(request, response_id: int):
    customer = customer_required(request)
    return ResponseService.accept_response(response_id, customer)
