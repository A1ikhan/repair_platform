from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from ninja_jwt.tokens import RefreshToken, AccessToken
from ninja.errors import HttpError
from back.models import CustomerProfile, WorkerProfile
from back.schemas import UserSchema
from back.services.user_service import ActivityService


class AuthService:
    @staticmethod
    def register_user(user_data, user_type: str, request=None):
        if User.objects.filter(username=user_data.username).exists():
            raise HttpError(400, "Username already exists")

        if User.objects.filter(email=user_data.email).exists():
            raise HttpError(400, "Email already exists")

        user = User.objects.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name or '',
            last_name=user_data.last_name or ''
        )

        if user_type == 'customer':
            CustomerProfile.objects.create(user=user)
        elif user_type == 'worker':
            WorkerProfile.objects.create(user=user)
        else:
            user.delete()
            raise HttpError(400, "Invalid user type")

        # Записываем действие в историю
        if request:
            ActivityService.record_activity(
                user=user,
                activity_type='register',
                description='Регистрация нового пользователя',
                request=request
            )

        return user

    @staticmethod
    def login_user(username: str, password: str, request=None):
        user = authenticate(username=username, password=password)
        if not user:
            raise HttpError(401, "Invalid credentials")

        # Записываем действие в историю
        if request:
            ActivityService.record_activity(
                user=user,
                activity_type='login',
                description='Вход в систему',
                request=request
            )

        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)

        return {
            "access": str(access),
            "refresh": str(refresh),
            "user": UserSchema.model_validate(user)
        }

    @staticmethod
    def refresh_token(refresh_token: str):
        try:
            refresh = RefreshToken(refresh_token)
            return {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
        except Exception:
            raise HttpError(401, "Invalid refresh token")

    @staticmethod
    def logout_user(user, request=None):
        """Выход пользователя с записью в историю"""
        if request and user.is_authenticated:
            ActivityService.record_activity(
                user=user,
                activity_type='logout',
                description='Выход из системы',
                request=request
            )

        return {"message": "Logged out successfully"}