from ninja import Router
from django.contrib.auth.models import User
from back.models import WorkerProfile
from back.schemas import UserSchema

router = Router(tags=["Workers"])

@router.get("/top", response=list[UserSchema], auth=None)
def get_top_workers(request):
    worker_ids = WorkerProfile.objects.filter(
        is_verified=True
    ).order_by('-rating').values_list('user_id', flat=True)[:10]

    return User.objects.filter(id__in=worker_ids)
