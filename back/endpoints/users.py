from typing import Optional

from ninja import File, UploadedFile, Router


from back.schemas import (
    UserDetailSchema, CustomerProfileUpdate, WorkerProfileUpdate,
    PasswordChangeSchema, AvatarUploadSchema, UserActivitySchema,
    UserStatsSchema
)
from back.services import UserProfileService, track_activity
from back.services.user_service import ActivityService

router=Router(tags=["users"])


# Эндпоинты профиля
@router.get("/profile/me", response=UserDetailSchema)
def get_my_profile(request):
    """Get current user profile"""
    return UserProfileService.get_user_profile(request.user)


@router.put("/profile/me/info", response=UserDetailSchema)
@track_activity('profile_update', 'Обновление основной информации')
def update_my_info(request, first_name: Optional[str] = None,
                   last_name: Optional[str] = None, email: Optional[str] = None):
    """Update user basic information"""
    data = {k: v for k, v in {
        'first_name': first_name,
        'last_name': last_name,
        'email': email
    }.items() if v is not None}

    user = UserProfileService.update_user_info(request.user, data)
    return user


@router.put("/profile/me/customer", response=UserDetailSchema)
@track_activity('profile_update', 'Обновление профиля клиента')
def update_my_customer_profile(request, data: CustomerProfileUpdate):
    """Update customer profile"""
    UserProfileService.update_customer_profile(request.user, data)
    return UserProfileService.get_user_profile(request.user)


@router.put("/profile/me/worker", response=UserDetailSchema)
@track_activity('profile_update', 'Обновление профиля работника')
def update_my_worker_profile(request, data: WorkerProfileUpdate):
    """Update worker profile"""
    UserProfileService.update_worker_profile(request.user, data)
    return UserProfileService.get_user_profile(request.user)


@router.post("/profile/me/avatar", response=AvatarUploadSchema)
@track_activity('avatar_update', 'Обновление аватара')
def upload_my_avatar(request, file: UploadedFile = File(...)):
    """Upload user avatar"""
    return UserProfileService.upload_avatar(request.user, file)


@router.post("/profile/me/password", response=dict)
@track_activity('password_change', 'Смена пароля')
def change_my_password(request, data: PasswordChangeSchema):
    """Change user password"""
    return UserProfileService.change_password(
        request.user, data.current_password, data.new_password
    )


# Эндпоинты истории действий
@router.get("/profile/me/activities", response=dict)
def get_my_activities(request, page: int = 1, page_size: int = 50):
    """Get user activity history"""
    return ActivityService.get_user_activities(request.user, page, page_size)


@router.get("/profile/me/activities/recent", response=list[UserActivitySchema])
def get_my_recent_activities(request, limit: int = 10):
    """Get recent user activities"""
    return ActivityService.get_recent_activities(request.user, limit)


# Эндпоинты статистики
@router.get("/profile/me/stats", response=UserStatsSchema)
def get_my_stats(request):
    """Get user statistics"""
    return UserProfileService.get_user_stats(request.user)




