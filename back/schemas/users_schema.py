from datetime import datetime
from typing import Optional, List

from ninja import Schema


class Message(Schema):
    message: str

class UserSchema(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    user_type: str

    @staticmethod
    def resolve_user_type(obj):
        if hasattr(obj, 'customer_profile'):
            return 'customer'
        elif hasattr(obj, 'worker_profile'):
            return 'worker'
        return 'unknown'

class UserCreate(Schema):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_type: str

class CustomerProfileSchema(Schema):
    phone_number: str
    address: str
    avatar_url: Optional[str]
    bio: str
    show_my_requests: bool
    show_my_responses: bool
    show_my_reviews: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_avatar_url(obj):
        if obj.avatar:
            return obj.avatar.url
        return None

class CustomerProfileUpdate(Schema):
    phone_number: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None
    show_my_requests: Optional[bool] = None
    show_my_responses: Optional[bool] = None
    show_my_reviews: Optional[bool] = None

class WorkerProfileSchema(Schema):
    phone_number: str
    specialization: str
    experience: int
    rating: float
    is_verified: bool
    avatar_url: Optional[str]
    bio: str
    show_my_responses: bool
    show_my_reviews: bool
    show_my_rating: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_avatar_url(obj):
        if obj.avatar:
            return obj.avatar.url
        return None

class WorkerProfileUpdate(Schema):
    phone_number: Optional[str] = None
    specialization: Optional[str] = None
    experience: Optional[int] = None
    bio: Optional[str] = None
    show_my_responses: Optional[bool] = None
    show_my_reviews: Optional[bool] = None
    show_my_rating: Optional[bool] = None

class UserDetailSchema(Schema):
    user: UserSchema
    customer_profile: Optional[CustomerProfileSchema] = None
    worker_profile: Optional[WorkerProfileSchema] = None

    @staticmethod
    def resolve_customer_profile(obj):
        if hasattr(obj, 'customer_profile'):
            return CustomerProfileSchema.from_orm(obj.customer_profile)
        return None

    @staticmethod
    def resolve_worker_profile(obj):
        if hasattr(obj, 'worker_profile'):
            return WorkerProfileSchema.from_orm(obj.worker_profile)
        return None

class UserActivitySchema(Schema):
    id: int
    activity_type: str
    activity_type_display: str
    description: str
    target_model: str
    target_id: Optional[int]
    created_at: datetime

    @staticmethod
    def resolve_activity_type_display(obj):
        return obj.get_activity_type_display()

class PasswordChangeSchema(Schema):
    current_password: str
    new_password: str

class AvatarUploadSchema(Schema):
    message: str
    avatar_url: Optional[str]

class UserStatsSchema(Schema):
    total_requests: int = 0
    total_responses: int = 0
    accepted_responses: int = 0
    completed_requests: int = 0
    average_rating: float = 0.0
    favorite_categories: List[str] = []

