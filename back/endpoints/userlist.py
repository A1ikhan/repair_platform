# Эндпоинты пользовательских списков
from ninja import Router

from back.schemas import RepairRequestSchemaOut
from back.schemas import UserListSchemaOut, ListItemSchemaOut, ListItemSchemaIn
from back.services import RepairRequestService
from back.services import UserListService

router = Router(tags=["UserList"])
@router.get("/lists", response=list[UserListSchemaOut], auth=None)
def get_my_lists(request):
    """Get all user lists"""
    return UserListService.get_user_lists(request.user)

@router.get("/lists/{list_name}", response=dict, auth=None)
def get_list_items(request):
    """Get items from specific list"""
    return UserListService.get_list_items(request.user)

@router.post("/lists/{list_name}/items", response=ListItemSchemaOut, auth=None)
def add_to_list(request, list_name: str, data: ListItemSchemaIn):
    """Add repair request to list"""
    return UserListService.add_to_list(
        request.user,
        list_name,
        data.repair_request_id,
        data.notes
    )

@router.delete("/lists/{list_name}/items/{repair_request_id}", response=dict, auth=None)
def remove_from_list(request, list_name: str, repair_request_id: int):
    """Remove repair request from list"""
    return UserListService.remove_from_list(request.user, list_name, repair_request_id)

@router.put("/lists/{list_name}/items/{repair_request_id}/notes", response=ListItemSchemaOut, auth=None)
def update_item_notes(request, list_name: str, repair_request_id: int, notes: str):
    """Update notes for list item"""
    return UserListService.update_list_item_notes(
        request.user, list_name, repair_request_id, notes
    )

@router.get("/lists/check/{repair_request_id}", response=dict, auth=None)
def check_in_list(request, repair_request_id: int, list_name: str = None):
    """Check if repair request is in user's list(s)"""
    is_in_list = UserListService.is_in_list(request.user, repair_request_id, list_name)
    return {
        "is_in_list": is_in_list,
        "repair_request_id": repair_request_id,
        "list_name": list_name
    }

@router.post("/lists/move", response=ListItemSchemaOut, auth=None)
def move_between_lists(
    request,
    repair_request_id: int,
    from_list: str,
    to_list: str
):
    """Move item between lists"""
    return UserListService.move_between_lists(
        request.user, repair_request_id, from_list, to_list
    )

# Специальные эндпоинты для частых операций
@router.get("/favorites", response=dict, auth=None)
def get_favorites(request):
    """Get user's favorite repair requests"""
    return UserListService.get_user_favorites(request.user)

@router.post("/favorites/{repair_request_id}", response=ListItemSchemaOut, auth=None)
def add_to_favorites(request, repair_request_id: int, notes: str = None):
    """Add repair request to favorites"""
    return UserListService.add_to_list(
        request.user, 'favorite', repair_request_id, notes
    )

@router.delete("/favorites/{repair_request_id}", response=dict, auth=None)
def remove_from_favorites(request, repair_request_id: int):
    """Remove repair request from favorites"""
    return UserListService.remove_from_list(request.user, 'favorite', repair_request_id)

# Эндпоинт для завершения заявок
@router.post("/repairs/{request_id}/complete", response=RepairRequestSchemaOut, auth=None)
def complete_repair_request(request, request_id: int):
    """Mark repair request as completed"""
    return RepairRequestService.complete_request(request_id, request.user)