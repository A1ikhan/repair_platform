from django.contrib.auth.models import User
from django.db import models
from ninja.errors import HttpError

from back.models import RepairRequest, Response, Review
from back.models.users_models import CustomerProfile, WorkerProfile, UserActivity


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

    @staticmethod
    def get_user_with_profile(user_id: int):
        try:
            user = User.objects.get(id=user_id)
            return user
        except User.DoesNotExist:
            raise HttpError(404, "User not found")

    @staticmethod
    def get_user_type(user):
        if hasattr(user, 'customer_profile'):
            return 'customer'
        elif hasattr(user, 'worker_profile'):
            return 'worker'
        return 'unknown'


class UserProfileService:
    @staticmethod
    def get_user_profile(user):
        return user

    @staticmethod
    def update_user_info(user, data: dict):
        update_fields = []
        for field in ['first_name', 'last_name', 'email']:
            if field in data and data[field] is not None:
                setattr(user, field, data[field])
                update_fields.append(field)

        if update_fields:
            user.save(update_fields=update_fields)

        return user

    @staticmethod
    def update_customer_profile(user, data):
        if not hasattr(user, 'customer_profile'):
            raise HttpError(400, "User is not a customer")

        profile = user.customer_profile
        update_fields = []
        for field, value in data.dict(exclude_unset=True).items():
            if hasattr(profile, field) and value is not None:
                setattr(profile, field, value)
                update_fields.append(field)

        if update_fields:
            profile.save(update_fields=update_fields)

        return profile

    @staticmethod
    def update_worker_profile(user, data):
        if not hasattr(user, 'worker_profile'):
            raise HttpError(400, "User is not a worker")

        profile = user.worker_profile
        update_fields = []
        for field, value in data.dict(exclude_unset=True).items():
            if hasattr(profile, field) and value is not None:
                setattr(profile, field, value)
                update_fields.append(field)

        if update_fields:
            profile.save(update_fields=update_fields)

        return profile

    @staticmethod
    def change_password(user, current_password: str, new_password: str):
        if not user.check_password(current_password):
            raise HttpError(400, "Current password is incorrect")

        user.set_password(new_password)
        user.save()
        return {"message": "Password changed successfully"}

    @staticmethod
    def upload_avatar(user, avatar_file):
        if hasattr(user, 'customer_profile'):
            profile = user.customer_profile
        elif hasattr(user, 'worker_profile'):
            profile = user.worker_profile
        else:
            raise HttpError(400, "User profile not found")

        if profile.avatar:
            profile.avatar.delete()

        profile.avatar = avatar_file
        profile.save()

        return {
            "message": "Avatar uploaded successfully",
            "avatar_url": profile.avatar.url if profile.avatar else None
        }

    @staticmethod
    def get_user_stats(user):


        stats = {
            'total_requests': 0,
            'total_responses': 0,
            'accepted_responses': 0,
            'completed_requests': 0,
            'average_rating': 0.0,
            'favorite_categories': []
        }

        if hasattr(user, 'customer_profile'):
            stats['total_requests'] = RepairRequest.objects.filter(created_by=user).count()
            stats['completed_requests'] = RepairRequest.objects.filter(
                created_by=user, status='completed'
            ).count()

            favorite_categories = RepairRequest.objects.filter(
                created_by=user
            ).values('device_type').annotate(
                count=models.Count('id')
            ).order_by('-count')[:3]
            stats['favorite_categories'] = [cat['device_type'] for cat in favorite_categories]

        if hasattr(user, 'worker_profile'):
            stats['total_responses'] = Response.objects.filter(worker=user).count()
            stats['accepted_responses'] = Response.objects.filter(
                worker=user, status='accepted'
            ).count()

            reviews = Review.objects.filter(worker=user)
            if reviews.exists():
                stats['average_rating'] = round(reviews.aggregate(
                    avg_rating=models.Avg('rating')
                )['avg_rating'], 1)

            favorite_categories = Response.objects.filter(
                worker=user
            ).values('repair_request__device_type').annotate(
                count=models.Count('id')
            ).order_by('-count')[:3]
            stats['favorite_categories'] = [cat['repair_request__device_type'] for cat in favorite_categories]

        return stats


class ActivityService:
    @staticmethod
    def record_activity(user, activity_type: str, description: str = "",
                        target_object=None, request=None):
        activity_data = {
            'user': user,
            'activity_type': activity_type,
            'description': description,
        }

        if target_object:
            activity_data['target_model'] = target_object.__class__.__name__.lower()
            activity_data['target_id'] = target_object.id

        if request:
            activity_data['ip_address'] = ActivityService.get_client_ip(request)
            activity_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')

        activity = UserActivity.objects.create(**activity_data)
        return activity

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def get_user_activities(user, page: int = 1, page_size: int = 50):
        from back.services.pagination_service import PaginationService
        activities = UserActivity.objects.filter(user=user)
        return PaginationService.paginate_queryset(activities, page, page_size)

    @staticmethod
    def get_recent_activities(user, limit: int = 10):
        return list(UserActivity.objects.filter(
            user=user
        ).order_by('-created_at')[:limit])


def track_activity(activity_type: str, description: str = ""):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            request = None
            user = None
            target_object = result if hasattr(result, 'id') else None

            for arg in args:
                if hasattr(arg, 'user') and hasattr(arg, 'META'):
                    request = arg
                    user = getattr(arg, 'user', None)
                    break

            if user and request:
                ActivityService.record_activity(
                    user=user,
                    activity_type=activity_type,
                    description=description,
                    target_object=target_object,
                    request=request
                )

            return result

        return wrapper

    return decorator