from django.core.cache import cache
from ninja import Router
from django.contrib.auth.models import User
from back.models import WorkerProfile
from back.schemas import UserSchema

router = Router(tags=["Workers"])

_TOP_WORKERS_CACHE_KEY = "top_workers_ids"
_CACHE_TTL = 5 * 60  # 5 minutes


@router.get("/top", response=list[UserSchema], auth=None)
def get_top_workers(request):
    worker_ids = cache.get(_TOP_WORKERS_CACHE_KEY)
    if worker_ids is None:
        worker_ids = list(
            WorkerProfile.objects.filter(is_verified=True)
            .order_by('-rating')
            .values_list('user_id', flat=True)[:10]
        )
        cache.set(_TOP_WORKERS_CACHE_KEY, worker_ids, _CACHE_TTL)

    return User.objects.filter(id__in=worker_ids).select_related(
        'worker_profile', 'customer_profile'
    )
