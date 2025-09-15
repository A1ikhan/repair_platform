from ninja import Router
from ..schemas import Message, UserCreate
from ..services import UserService

router = Router()

@router.post('/register', response={200: Message, 400: Message}, auth=None)
def register(request, data: UserCreate):
    """Register new user"""
    UserService.create_user(data, data.user_type)
    return 200, {"message": "User created successfully"}