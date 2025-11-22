from typing import List, Dict

from ninja.errors import HttpError
from back.models.repair_requests_models import RepairRequest, RepairRequestFile, ProblemPhoto, PriceHistory
from back.models import Response
from back.services.userlist_service import AutoListService
from django.db import models


class DataCollectionService:
    """Сервис для сбора данных для будущего ИИ"""

    @staticmethod
    def create_price_history(repair_request: RepairRequest):
        """Создать запись в истории цен"""
        price_history = PriceHistory.objects.create(
            repair_request=repair_request,
            device_type=repair_request.device_type,
            problem_description=repair_request.description,
            final_price=None
        )
        return price_history

    @staticmethod
    def update_final_price(repair_request_id: int, final_price: float):
        """Обновить финальную цену в истории"""
        try:
            repair_request = RepairRequest.objects.get(id=repair_request_id)
            repair_request.final_price = final_price
            repair_request.save()

            price_history = PriceHistory.objects.get(repair_request=repair_request)
            price_history.final_price = final_price
            price_history.save()

            return True
        except (RepairRequest.DoesNotExist, PriceHistory.DoesNotExist):
            return False

    @staticmethod
    def extract_keywords(description: str) -> List[str]:
        """Извлечение ключевых слов из описания"""
        import re
        stop_words = {'сломан', 'не', 'работает', 'ремонт', 'нужен', 'помощь', 'починить'}

        words = re.findall(r'\b[а-яa-z]+\b', description.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        return list(set(keywords))[:10]

    @staticmethod
    def analyze_problem_complexity(description: str, device_type: str) -> Dict:
        """Анализ сложности проблемы"""
        complexity_keywords = {
            'high': ['замена', 'двигатель', 'компрессор', 'плата', 'контроллер', 'прошивка'],
            'medium': ['течет', 'шумит', 'негреет', 'неохлаждает', 'засор', 'фильтр'],
            'low': ['кнопка', 'дверца', 'шнур', 'вилка', 'настройка']
        }

        description_lower = description.lower()
        complexity_score = 0
        detected_complexities = []

        for level, keywords in complexity_keywords.items():
            for keyword in keywords:
                if keyword in description_lower:
                    detected_complexities.append(keyword)
                    if level == 'high':
                        complexity_score += 3
                    elif level == 'medium':
                        complexity_score += 2
                    else:
                        complexity_score += 1

        return {
            'complexity_score': min(complexity_score, 10),
            'detected_keywords': detected_complexities,
            'estimated_time_hours': max(1, complexity_score * 0.5)
        }

    @staticmethod
    def get_training_data_stats():
        """Статистика собранных данных"""
        total_requests = RepairRequest.objects.count()
        completed_with_price = RepairRequest.objects.filter(
            status='completed',
            final_price__isnull=False
        ).count()

        price_histories = PriceHistory.objects.filter(final_price__isnull=False)

        return {
            'total_requests': total_requests,
            'completed_with_price': completed_with_price,
            'price_history_records': price_histories.count(),
            'ready_for_training': completed_with_price >= 50,
            'average_price': price_histories.aggregate(
                avg_price=models.Avg('final_price')
            )['avg_price'] or 0
        }


class SimplePriceEstimator:
    """Простой оценщик цен (временное решение до ИИ)"""

    BASE_PRICES = {
        'fridge': 3000,
        'washer': 2500,
        'oven': 2000,
        'dishwasher': 2200,
        'other': 1500
    }

    @staticmethod
    def estimate_price(device_type: str, description: str) -> Dict:
        """Простая оценка цены на основе правил"""
        base_price = SimplePriceEstimator.BASE_PRICES.get(device_type, 1500)

        complexity_analysis = DataCollectionService.analyze_problem_complexity(description, device_type)
        complexity_multiplier = 1.0 + (complexity_analysis['complexity_score'] * 0.1)
        estimated_price = base_price * complexity_multiplier

        return {
            'predicted_price': round(estimated_price, 2),
            'confidence': 0.3,
            'price_range': {
                'min': round(estimated_price * 0.5, 2),
                'max': round(estimated_price * 1.5, 2)
            },
            'complexity_analysis': complexity_analysis,
            'message': 'Примерная оценка на основе типа устройства и сложности проблемы'
        }


class RepairRequestService:
    @staticmethod
    def get_all_requests():
        return RepairRequest.objects.select_related('created_by').prefetch_related('files', 'problem_photos').all()

    @staticmethod
    def get_request_by_id(request_id: int):
        try:
            return RepairRequest.objects.select_related('created_by').prefetch_related('files', 'problem_photos').get(
                id=request_id)
        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def get_user_requests(user):
        return RepairRequest.objects.filter(created_by=user).select_related('created_by').prefetch_related('files',
                                                                                                           'problem_photos')

    @staticmethod
    def create_request(data, user, files: list = None, file_descriptions: list = None, is_public: bool = True):
        # Создаем саму заявку
        repair_request = RepairRequest.objects.create(
            **data.dict(),
            created_by=user,
            status='new'
        )

        # НОВОЕ: Сбор данных для ИИ
        DataCollectionService.create_price_history(repair_request)

        # НОВОЕ: Простая оценка цены
        price_estimation = SimplePriceEstimator.estimate_price(
            data.device_type,
            data.description
        )

        repair_request.predicted_price = price_estimation['predicted_price']
        repair_request.price_confidence = price_estimation['confidence']
        repair_request.ai_analysis_data = price_estimation
        repair_request.save()

        # Существующая логика файлов
        if files:
            for i, file in enumerate(files):
                RepairRequestFile.objects.create(
                    repair_request=repair_request,
                    file=file,
                    uploaded_by=user,
                    description=(file_descriptions[i] if file_descriptions and i < len(file_descriptions) else ''),
                    is_public=is_public
                )

        return repair_request

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
    def complete_request(request_id: int, user):
        """Завершить заявку (только автор или принятый работник)"""
        try:
            repair_request = RepairRequest.objects.get(id=request_id)

            can_complete = (
                    user == repair_request.created_by or
                    Response.objects.filter(
                        repair_request=repair_request,
                        worker=user,
                        status='accepted'
                    ).exists()
            )

            if not can_complete:
                raise HttpError(403, "No permission to complete this request")

            repair_request.status = 'completed'
            repair_request.save()

            # Автоматически управляем списками
            AutoListService.handle_request_completed(repair_request)

            return repair_request
        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def delete_request(request_id: int, user):
        try:
            repair_request = RepairRequest.objects.get(id=request_id, created_by=user)
            repair_request.delete()
            return {"message": "Repair request deleted successfully"}
        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found or you don't have permission")

    @staticmethod
    def search_requests(search_term: str = None, device_type: str = None, status: str = None):
        queryset = RepairRequest.objects.select_related('created_by').prefetch_related('files', 'problem_photos')

        if search_term:
            queryset = queryset.filter(
                models.Q(title__icontains=search_term) |
                models.Q(description__icontains=search_term)
            )
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    @staticmethod
    def get_available_filters():
        return {
            'device_types': [choice[0] for choice in RepairRequest.DEVICE_TYPES],
            'statuses': [choice[0] for choice in RepairRequest.STATUS_CHOICES]
        }

    # НОВЫЕ МЕТОДЫ ДЛЯ ИИ
    @staticmethod
    def add_problem_photo(repair_request_id: int, image_file, description: str, user):
        """Добавить фото проблемы к заявке"""
        try:
            repair_request = RepairRequest.objects.get(id=repair_request_id)

            if repair_request.created_by != user:
                raise HttpError(403, "Only request owner can add photos")

            photo = ProblemPhoto.objects.create(
                image=image_file,
                uploaded_by=user,
                description=description or ""
            )

            repair_request.problem_photos.add(photo)
            return photo

        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def update_final_price(repair_request_id: int, final_price: float, user):
        """Обновить финальную цену после ремонта"""
        try:
            repair_request = RepairRequest.objects.get(id=repair_request_id)

            can_update = (
                    repair_request.created_by == user
                    # repair_request.responses.filter(worker=user, status='accepted').exists()
            )

            if not can_update:
                raise HttpError(403, "No permission to update final price")

            DataCollectionService.update_final_price(repair_request_id, final_price)

            return repair_request

        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def get_problem_analysis(repair_request_id: int):
        """Анализ проблемы (ключевые слова и сложность)"""
        repair_request = RepairRequestService.get_request_by_id(repair_request_id)

        keywords = DataCollectionService.extract_keywords(repair_request.description)
        complexity = DataCollectionService.analyze_problem_complexity(
            repair_request.description, repair_request.device_type
        )

        return {
            'keywords': keywords,
            'complexity_analysis': complexity,
            'device_type': repair_request.device_type
        }