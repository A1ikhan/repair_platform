from ninja import Router
from typing import List
from ...services import RepairRequestService
from ...schemas import RepairRequestSchemaIn, RepairRequestSchemaOut
from ...dependencies import customer_required

router = Router()

@router.get('/', response=List[RepairRequestSchemaOut], auth=None)
def list_repair_requests(request):
    """Get all repair requests"""
    return RepairRequestService.get_all_requests()

@router.get('/{request_id}', response=RepairRequestSchemaOut, auth=None)
def get_repair_request(request, request_id: int):
    """Get specific repair request"""
    return RepairRequestService.get_request_by_id(request_id)

@router.get('/my-requests', response=List[RepairRequestSchemaOut], auth=None)
def get_my_requests(request):
    """Get current user's repair requests"""
    return RepairRequestService.get_user_requests(request.user)

@router.post('/', response=RepairRequestSchemaOut, auth=None)
def create_repair_request(request, data: RepairRequestSchemaIn):
    """Create new repair request (customer only)"""
    customer = customer_required(request)
    return RepairRequestService.create_request(data, customer)

@router.put('/{request_id}', response=RepairRequestSchemaOut, auth=None)
def update_repair_request(request, request_id: int, data: RepairRequestSchemaIn):
    """Update repair request (only author)"""
    return RepairRequestService.update_request(request_id, data, request.user)

@router.delete('/{request_id}', response=dict, auth=None)
def delete_repair_request(request, request_id: int):
    """Delete repair request (only author)"""
    return RepairRequestService.delete_request(request_id, request.user)