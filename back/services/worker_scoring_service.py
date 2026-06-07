import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

_WEIGHTS = {
    'rating': 0.35,
    'distance': 0.30,
    'experience': 0.15,
    'specialization': 0.10,
    'availability': 0.05,
    'verification': 0.05,
}

# Keywords that indicate a worker's specialization matches a device type
_DEVICE_KEYWORDS = {
    'fridge': ['холодильник', 'холод', 'fridge', 'refrigerator'],
    'washer': ['стиральн', 'washer', 'washing'],
    'oven': ['духовк', 'плит', 'oven', 'stove', 'печ'],
    'dishwasher': ['посудомоечн', 'dishwasher'],
    'microwave': ['микроволн', 'microwave'],
    'tv': ['телевизор', 'tv', 'телев'],
    'ac': ['кондиционер', 'кондиц', 'ac', 'air condition'],
    'vacuum': ['пылесос', 'vacuum'],
    'iron': ['утюг', 'iron'],
    'other': [],
}


class WorkerScoringService:

    @staticmethod
    def calculate_score(
        rating: float,
        distance_km: float,
        max_distance_km: float,
        experience: int,
        is_verified: bool,
        specialization: str,
        active_count: int,
        device_type: Optional[str] = None,
    ) -> float:
        rating_score = rating / 5.0

        distance_score = max(0.0, 1.0 - (distance_km / max(max_distance_km, 1)))

        # Cap at 10 years of experience
        experience_score = min(experience / 10.0, 1.0)

        verification_score = 1.0 if is_verified else 0.0

        specialization_score = WorkerScoringService._specialization_match(specialization, device_type)

        # 5+ active repairs = fully booked
        availability_score = max(0.0, 1.0 - (active_count / 5))

        score = (
            rating_score * _WEIGHTS['rating'] +
            distance_score * _WEIGHTS['distance'] +
            experience_score * _WEIGHTS['experience'] +
            specialization_score * _WEIGHTS['specialization'] +
            availability_score * _WEIGHTS['availability'] +
            verification_score * _WEIGHTS['verification']
        )

        return round(score, 3)

    @staticmethod
    def _specialization_match(specialization: str, device_type: Optional[str]) -> float:
        if not device_type:
            return 0.5
        keywords = _DEVICE_KEYWORDS.get(device_type, [])
        spec_lower = specialization.lower()
        if any(kw in spec_lower for kw in keywords):
            return 1.0
        if device_type.lower() in spec_lower:
            return 1.0
        return 0.3

    @staticmethod
    def score_workers(
        workers_data: List[Dict],
        max_distance_km: float,
        device_type: Optional[str] = None,
    ) -> List[Dict]:
        """Add a composite score to each worker dict and sort by score descending."""
        if not workers_data:
            return []

        worker_ids = [w['worker_id'] for w in workers_data]

        from back.models.response_models import Response
        from django.db.models import Count

        active_counts = dict(
            Response.objects.filter(
                worker_id__in=worker_ids,
                status='accepted',
                repair_request__status='active',
            )
            .values('worker_id')
            .annotate(cnt=Count('id'))
            .values_list('worker_id', 'cnt')
        )

        for worker in workers_data:
            worker['score'] = WorkerScoringService.calculate_score(
                rating=worker.get('rating', 0.0),
                distance_km=worker['distance_km'],
                max_distance_km=max_distance_km,
                experience=worker.get('experience', 0),
                is_verified=worker.get('is_verified', False),
                specialization=worker.get('specialization', ''),
                active_count=active_counts.get(worker['worker_id'], 0),
                device_type=device_type,
            )

        workers_data.sort(key=lambda x: x['score'], reverse=True)
        return workers_data
