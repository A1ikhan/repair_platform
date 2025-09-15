# api/dependencies.py
from django.http import HttpRequest
from ninja.security import HttpBearer
from ninja_jwt.tokens import Token
from django.contrib.auth.models import User
from ninja.errors import HttpError

class AuthBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        try:
            validated_token = Token(token)
            user_id = validated_token.payload.get('user_id')
            user = User.objects.get(id=user_id)
            request.user = user  # Добавляем пользователя в request
            return user
        except Exception:
            raise HttpError(401, "Invalid or expired token")

# Дополнительные зависимости
def get_current_user(request):
    """Зависимость для получения текущего пользователя"""
    return request.user

def customer_required(request):
    """Зависимость для проверки, что пользователь - клиент"""
    user = request.user
    if not hasattr(user, 'customer_profile'):
        raise HttpError(403, "Only customers can perform this action")
    return user

def worker_required(request):
    """Зависимость для проверки, что пользователь - работник"""
    user = request.user
    if not hasattr(user, 'worker_profile'):
        raise HttpError(403, "Only workers can perform this action")
    return user