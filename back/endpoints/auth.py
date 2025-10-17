from ninja import Router
from back.schemas import Message, UserCreate, LoginInput, TokenOutput
from back.services.auth_service import AuthService

router = Router(tags=["Auth"])

@router.post("/register", response={200: Message, 400: Message}, auth=None)
def register(request, data: UserCreate):
    """Register new user with activity tracking"""
    AuthService.register_user(data, data.user_type, request)
    return 200, {"message": "User created successfully"}

@router.post("/login", response=TokenOutput, auth=None)
def login(request, data: LoginInput):
    """Login user with activity tracking"""
    return AuthService.login_user(data.username, data.password, request)

@router.post("/refresh", response=TokenOutput, auth=None)
def refresh_token(request, refresh_token: str):
    """Refresh JWT token"""
    return AuthService.refresh_token(refresh_token)

@router.post("/logout", response=Message)
def logout(request):
    """Logout user with activity tracking"""
    return AuthService.logout_user(request.user, request)