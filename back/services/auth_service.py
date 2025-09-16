from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from ninja_jwt.tokens import RefreshToken
from ninja.errors import HttpError
from back.models import CustomerProfile, WorkerProfile


class AuthService:
    @staticmethod
    def register_user(user_data, user_type: str):
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

        return user

    @staticmethod
    def login_user(username: str, password: str):
        user = authenticate(username=username, password=password)
        if not user:
            raise HttpError(401, "Invalid credentials")

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
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
