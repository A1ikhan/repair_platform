# api/routers/responses.py
from ninja import Router
from typing import List
from ..services  import ResponseService
from ..schemas import ResponseSchemaIn, ResponseSchemaOut
from ..dependencies import worker_required, customer_required

router = Router()

@router.post('/request/{repair_request_id}', response=ResponseSchemaOut, auth=None)
def create_response(request, repair_request_id: int, data: ResponseSchemaIn):
    """Create response to repair request (worker only)"""
    worker = worker_required(request)
    return ResponseService.create_response(repair_request_id, data, worker)

@router.get('/request/{repair_request_id}', response=List[ResponseSchemaOut], auth=None)
def get_responses_for_request(request, repair_request_id: int):
    """Get all responses for specific repair request"""
    return ResponseService.get_responses_for_request(repair_request_id, request.user)

@router.get('/my-responses', response=List[ResponseSchemaOut], auth=None)
def get_my_responses(request):
    """Get all responses of current worker"""
    worker = worker_required(request)
    return ResponseService.get_worker_responses(worker)

@router.post('/{response_id}/accept', response=ResponseSchemaOut, auth=None)
def accept_response(request, response_id: int):
    """Accept response (customer only)"""
    customer = customer_required(request)
    return ResponseService.accept_response(response_id, customer)