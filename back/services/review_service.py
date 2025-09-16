from django.contrib.auth.models import User
from ninja.errors import HttpError
from django.db import models
from back.models import RepairRequest, Review
from back import models as api_models


class ReviewService:
    @staticmethod
    def create_review(repair_request_id: int, data, customer):
        try:
            repair_request = RepairRequest.objects.get(
                id=repair_request_id,
                created_by=customer,
                status='completed'
            )

            accepted_response = api_models.Response.objects.get(
                repair_request=repair_request,
                status='accepted'
            )

            review, created = Review.objects.get_or_create(
                repair_request=repair_request,
                customer=customer,
                worker=accepted_response.worker,
                defaults={'rating': data.rating, 'comment': data.comment or ''}
            )

            if not created:
                review.rating = data.rating
                review.comment = data.comment or ''
                review.save()

            ReviewService._update_worker_rating(accepted_response.worker)
            return review

        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found or not completed")
        except api_models.Response.DoesNotExist:
            raise HttpError(400, "No accepted response for this request")

    @staticmethod
    def _update_worker_rating(worker):
        reviews = Review.objects.filter(worker=worker)
        if reviews.exists():
            avg_rating = reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating']
            worker.worker_profile.rating = round(avg_rating, 1)
            worker.worker_profile.save()

    @staticmethod
    def get_worker_reviews(worker_id: int):
        try:
            worker = User.objects.get(id=worker_id)
            return Review.objects.filter(worker=worker).select_related('customer')
        except User.DoesNotExist:
            raise HttpError(404, "Worker not found")
