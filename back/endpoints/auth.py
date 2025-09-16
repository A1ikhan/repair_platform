from ninja import Router
from back.schemas import Message, UserCreate, LoginInput, TokenOutput
from back.services import AuthService

router = Router(tags=["Auth"])

@router.post("/register", response={200: Message, 400: Message}, auth=None)
def register(request, data: UserCreate):
    AuthService.register_user(data, data.user_type)
    return 200, {"message": "User created successfully"}

@router.post("/login", response=TokenOutput, auth=None)
def login(request, data: LoginInput):
    return AuthService.login_user(data.username, data.password)

@router.post("/refresh", response=TokenOutput, auth=None)
def refresh_token(request, refresh_token: str):
    return AuthService.refresh_token(refresh_token)
