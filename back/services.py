# api/services.py
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from ninja.responses import Response
from ninja_jwt.tokens import RefreshToken

from .models import RepairRequest, CustomerProfile, WorkerProfile
from typing import Optional, List
from ninja.errors import HttpError


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
            access_token = refresh.access_token
            return {
                "access": str(access_token),
                "refresh": str(refresh)
            }
        except Exception:
            raise HttpError(401, "Invalid refresh token")
class UserService:
    @staticmethod
    def create_user(user_data, user_type: str):
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


class RepairRequestService:
    @staticmethod
    def get_all_requests():
        return RepairRequest.objects.select_related('created_by').all()

    @staticmethod
    def get_request_by_id(request_id: int):
        try:
            return RepairRequest.objects.select_related('created_by').get(id=request_id)
        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def get_user_requests(user):
        return RepairRequest.objects.filter(created_by=user).select_related('created_by')

    @staticmethod
    def create_request(data, user):
        return RepairRequest.objects.create(
            **data.dict(),
            created_by=user,
            status='new'
        )

    @staticmethod
    def update_request(request_id: int, data, user):
        try:
            repair_request = RepairRequest.objects.get(id=request_id, created_by=user)
            for attr, value in data.dict().items():
                setattr(repair_request, attr, value)
            repair_request.save()
            return repair_request
        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found or you don't have permission")

    @staticmethod
    def delete_request(request_id: int, user):
        try:
            repair_request = RepairRequest.objects.get(id=request_id, created_by=user)
            repair_request.delete()
            return {"message": "Repair request deleted successfully"}
        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found or you don't have permission")


class ResponseService:
    @staticmethod
    def create_response(repair_request_id: int, data, worker):
        try:
            repair_request = RepairRequest.objects.get(id=repair_request_id)
            # Проверяем, что работник еще не откликался на эту заявку
            if Response.objects.filter(repair_request=repair_request, worker=worker).exists():
                raise HttpError(400, "You have already responded to this request")

            return Response.objects.create(
                repair_request=repair_request,
                worker=worker,
                message=data.message,
                proposed_price=data.proposed_price,
                status='sent'
            )
        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def get_responses_for_request(repair_request_id: int, user):
        try:
            repair_request = RepairRequest.objects.get(id=repair_request_id)
            # Проверяем права: либо автор заявки, либо работник, который откликался
            if repair_request.created_by != user and not Response.objects.filter(repair_request=repair_request,
                                                                                 worker=user).exists():
                raise HttpError(403, "Access denied")

            return Response.objects.filter(repair_request=repair_request).select_related('worker')
        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def get_worker_responses(worker):
        return Response.objects.filter(worker=worker).select_related('repair_request')

    @staticmethod
    def accept_response(response_id: int, customer):
        try:
            response = Response.objects.get(id=response_id)
            # Проверяем, что пользователь - автор заявки
            if response.repair_request.created_by != customer:
                raise HttpError(403, "Only the request owner can accept responses")

            response.status = 'accepted'
            response.save()

            # Меняем статус заявки и отклоняем другие отклики
            response.repair_request.status = 'active'
            response.repair_request.save()

            Response.objects.filter(
                repair_request=response.repair_request
            ).exclude(id=response_id).update(status='rejected')

            return response
        except Response.DoesNotExist:
            raise HttpError(404, "Response not found")