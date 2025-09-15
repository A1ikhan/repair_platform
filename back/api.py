# api/api.py
from ninja import NinjaAPI
from .schemas import (
    Message, UserCreate, LoginInput, TokenOutput,
    RepairRequestSchemaIn, RepairRequestSchemaOut,
    ResponseSchemaIn, ResponseSchemaOut
)
from .services import AuthService, RepairRequestService, ResponseService
from .dependencies import AuthBearer, customer_required, worker_required

# Создаем основной экземпляр NinjaAPI
api = NinjaAPI(
    title="Repair Platform API",
    version="1.0.0",
    description="API for appliance repair service platform",
    auth=AuthBearer(),
    csrf=True,
)

# Эндпоинты аутентификации
@api.post("/auth/register", response={200: Message, 400: Message}, auth=None)
def register(request, data: UserCreate):
    """Register new user"""
    AuthService.register_user(data, data.user_type)
    return 200, {"message": "User created successfully"}

@api.post("/auth/login", response=TokenOutput, auth=None)
def login(request, data: LoginInput):
    """Login user"""
    return AuthService.login_user(data.username, data.password)

@api.post("/auth/refresh", response=TokenOutput, auth=None)
def refresh_token(request, refresh_token: str):
    """Refresh JWT token"""
    return AuthService.refresh_token(refresh_token)

# Эндпоинты заявок
@api.get("/repairs", response=list[RepairRequestSchemaOut], auth=None)
def list_repair_requests(request):
    """Get all repair requests"""
    return RepairRequestService.get_all_requests()

@api.get("/repairs/{request_id}", response=RepairRequestSchemaOut, auth=None)
def get_repair_request(request, request_id: int):
    """Get specific repair request"""
    return RepairRequestService.get_request_by_id(request_id)

@api.get("/repairs/my/requests", response=list[RepairRequestSchemaOut], auth=None)
def get_my_requests(request):
    """Get current user's repair requests"""
    return RepairRequestService.get_user_requests(request.user)

@api.post("/repairs", response=RepairRequestSchemaOut, auth=None)
def create_repair_request(request, data: RepairRequestSchemaIn):
    """Create new repair request (customer only)"""
    customer = customer_required(request)
    return RepairRequestService.create_request(data, customer)

@api.put("/repairs/{request_id}", response=RepairRequestSchemaOut, auth=None)
def update_repair_request(request, request_id: int, data: RepairRequestSchemaIn):
    """Update repair request (only author)"""
    return RepairRequestService.update_request(request_id, data, request.user)

@api.delete("/repairs/{request_id}", response=dict, auth=None)
def delete_repair_request(request, request_id: int):
    """Delete repair request (only author)"""
    return RepairRequestService.delete_request(request_id, request.user)

# Эндпоинты откликов
@api.post("/responses/request/{repair_request_id}", response=ResponseSchemaOut, auth=None)
def create_response(request, repair_request_id: int, data: ResponseSchemaIn):
    """Create response to repair request (worker only)"""
    worker = worker_required(request)
    return ResponseService.create_response(repair_request_id, data, worker)

@api.get("/responses/request/{repair_request_id}", response=list[ResponseSchemaOut], auth=None)
def get_responses_for_request(request, repair_request_id: int):
    """Get all responses for specific repair request"""
    return ResponseService.get_responses_for_request(repair_request_id, request.user)

@api.get("/responses/my", response=list[ResponseSchemaOut], auth=None)
def get_my_responses(request):
    """Get all responses of current worker"""
    worker = worker_required(request)
    return ResponseService.get_worker_responses(worker)

@api.post("/responses/{response_id}/accept", response=ResponseSchemaOut, auth=None)
def accept_response(request, response_id: int):
    """Accept response (customer only)"""
    customer = customer_required(request)
    return ResponseService.accept_response(response_id, customer)

# Тестовые эндпоинты
@api.get("/protected/test", auth=None)
def test_protected(request):
    """Test protected endpoint"""
    return {"message": f"Hello {request.user.username}! You are authenticated."}

@api.get("/public/hello", auth=None)
def hello_public(request):
    """Public endpoint"""
    return {"message": "Hello from Repair Platform API!"}