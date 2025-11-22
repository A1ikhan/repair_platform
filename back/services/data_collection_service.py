from django.db import models
from ninja.errors import HttpError
import re
from typing import List, Dict
from back.models.repair_models import RepairRequest, PriceHistory, ProblemPhoto


class DataCollectionService:
    """Сервис для сбора и подготовки данных для будущего ИИ"""

    @staticmethod
    def create_price_history(repair_request: RepairRequest):
        """Создать запись в истории цен"""
        price_history = PriceHistory.objects.create(
            repair_request=repair_request,
            device_type=repair_request.device_type,
            problem_description=repair_request.description,
            final_price=None  # Пока неизвестно
        )
        return price_history

    @staticmethod
    def update_final_price(repair_request_id: int, final_price: float):
        """Обновить финальную цену в истории"""
        try:
            repair_request = RepairRequest.objects.get(id=repair_request_id)
            repair_request.final_price = final_price
            repair_request.save()

            # Обновляем историю цен
            price_history = PriceHistory.objects.get(repair_request=repair_request)
            price_history.final_price = final_price
            price_history.save()

            return True

        except (RepairRequest.DoesNotExist, PriceHistory.DoesNotExist):
            return False

    @staticmethod
    def extract_keywords(description: str) -> List[str]:
        """Извлечение ключевых слов из описания проблемы"""
        # Простая обработка текста для будущего ИИ
        stop_words = {'сломан', 'не', 'работает', 'ремонт', 'нужен', 'помощь', 'починить'}

        words = re.findall(r'\b[а-яa-z]+\b', description.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        return list(set(keywords))[:10]  # Уникальные слова, максимум 10

    @staticmethod
    def analyze_problem_complexity(description: str, device_type: str) -> Dict:
        """Простой анализ сложности проблемы (для будущего ИИ)"""
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
        """Статистика собранных данных для обучения"""
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
            'ready_for_training': completed_with_price >= 50,  # Минимум для обучения
            'average_price': price_histories.aggregate(
                avg_price=models.Avg('final_price')
            )['avg_price'] or 0
        }


class SimplePriceEstimator:
    """Простой оценщик цен на основе правил (временное решение до ИИ)"""

    BASE_PRICES = {
        'fridge': 30000,
        'washer': 25000,
        'oven': 20000,
        'dishwasher': 22000,
        'other': 15000
    }

    @staticmethod
    def estimate_price(device_type: str, description: str) -> Dict:
        """Простая оценка цены на основе правил"""
        base_price = SimplePriceEstimator.BASE_PRICES.get(device_type, 1500)

        # Анализ сложности
        complexity_analysis = DataCollectionService.analyze_problem_complexity(description, device_type)

        # Корректировка цены на основе сложности
        complexity_multiplier = 1.0 + (complexity_analysis['complexity_score'] * 0.1)
        estimated_price = base_price * complexity_multiplier

        return {
            'predicted_price': round(estimated_price, 2),
            'confidence': 0.3,  # Низкая уверенность без ИИ
            'price_range': {
                'min': round(estimated_price * 0.5, 2),
                'max': round(estimated_price * 1.5, 2)
            },
            'complexity_analysis': complexity_analysis,
            'message': 'Примерная оценка на основе типа устройства и сложности проблемы'
        }