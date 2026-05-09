from django.contrib.auth.models import User
from django.db.models import Q
from ninja.errors import HttpError
from back.models import WorkerProfile, SavedWorker


class WorkerService:
    @staticmethod
    def list_workers(specialization: str = None, is_verified: bool = None, search: str = None):
        qs = User.objects.filter(
            worker_profile__isnull=False
        ).select_related('worker_profile', 'customer_profile').order_by('-worker_profile__rating')

        if is_verified is not None:
            qs = qs.filter(worker_profile__is_verified=is_verified)

        if specialization:
            qs = qs.filter(worker_profile__specialization__icontains=specialization)

        if search:
            qs = qs.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        return qs

    @staticmethod
    def get_worker_by_id(worker_id: int):
        try:
            return User.objects.select_related('worker_profile', 'customer_profile').get(
                id=worker_id, worker_profile__isnull=False
            )
        except User.DoesNotExist:
            raise HttpError(404, "Worker not found")

    @staticmethod
    def save_worker(customer, worker_id: int):
        worker = WorkerService.get_worker_by_id(worker_id)
        if customer.id == worker.id:
            raise HttpError(400, "You cannot save yourself")
        _, created = SavedWorker.objects.get_or_create(customer=customer, worker=worker)
        if not created:
            raise HttpError(400, "Worker already saved")
        return worker

    @staticmethod
    def unsave_worker(customer, worker_id: int):
        deleted, _ = SavedWorker.objects.filter(customer=customer, worker_id=worker_id).delete()
        if not deleted:
            raise HttpError(404, "Saved worker not found")

    @staticmethod
    def get_saved_workers(customer):
        worker_ids = SavedWorker.objects.filter(customer=customer).values_list('worker_id', flat=True)
        return User.objects.filter(id__in=worker_ids).select_related('worker_profile', 'customer_profile')
