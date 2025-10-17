import os
from typing import Optional, Dict, List

import requests
from ninja.errors import HttpError


class DGisService:
    """Сервис для работы с 2GIS API"""

    BASE_URL = "https://catalog.api.2gis.com/3.0"
    GEOCODE_URL = "https://geo.api.2gis.com/3.0"

    def __init__(self):
        self.api_key = os.getenv('DGIS_API_KEY')
        if not self.api_key:
            raise Exception("DGIS_API_KEY not found in environment variables")

    def geocode_address(self, address: str, city: str = None) -> Optional[Dict]:
        """
        Геокодирование адреса - преобразование текста в координаты
        """
        url = f"{self.GEOCODE_URL}/geocode"
        params = {
            'q': address,
            'key': self.api_key,
            'fields': 'items.point,items.full_name'
        }

        if city:
            params['region'] = city

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('result') and data['result'].get('items'):
                first_result = data['result']['items'][0]
                return {
                    'latitude': first_result['point']['lat'],
                    'longitude': first_result['point']['lon'],
                    'full_address': first_result['full_name'],
                    'confidence': 'high'
                }

            return None

        except requests.exceptions.RequestException as e:
            print(f"2GIS Geocoding error: {e}")
            return None

    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Обратное геокодирование - координаты в адрес
        """
        url = f"{self.GEOCODE_URL}/reverse"
        params = {
            'lat': lat,
            'lon': lon,
            'key': self.api_key,
            'fields': 'items.full_name'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('result') and data['result'].get('items'):
                return data['result']['items'][0]['full_name']

            return None

        except requests.exceptions.RequestException as e:
            print(f"2GIS Reverse Geocoding error: {e}")
            return None

    def search_businesses(self, query: str, lat: float, lon: float, radius: int = 1000) -> List[Dict]:
        """
        Поиск бизнесов/организаций поблизости
        """
        url = f"{self.BASE_URL}/items"
        params = {
            'q': query,
            'key': self.api_key,
            'location': f"{lon},{lat}",
            'radius': radius,
            'sort': 'distance',
            'fields': 'items.point,items.name,items.address_name,items.contacts',
            'limit': 20
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            if data.get('result') and data['result'].get('items'):
                for item in data['result']['items']:
                    results.append({
                        'name': item.get('name', ''),
                        'address': item.get('address_name', ''),
                        'latitude': item['point']['lat'],
                        'longitude': item['point']['lon'],
                        'contacts': item.get('contacts', []),
                        'distance': None
                    })

            return results

        except requests.exceptions.RequestException as e:
            print(f"2GIS Business search error: {e}")
            return []

    def calculate_distance_matrix(self, origins: List[tuple], destinations: List[tuple]) -> Optional[Dict]:
        """
        Матрица расстояний между точками
        """
        if not origins or not destinations:
            return None

        return self._calculate_straight_distance_matrix(origins, destinations)

    def _calculate_straight_distance_matrix(self, origins: List[tuple], destinations: List[tuple]) -> Dict:
        """Расчет расстояний по прямой (в км)"""
        from math import radians, sin, cos, sqrt, atan2

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Земной радиус в км
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            return R * c

        matrix = {}
        for i, origin in enumerate(origins):
            matrix[i] = {}
            for j, destination in enumerate(destinations):
                distance = haversine(origin[0], origin[1], destination[0], destination[1])
                matrix[i][j] = round(distance, 2)

        return matrix


class LocationService:
    """Высокоуровневый сервис для работы с локациями"""

    @staticmethod
    def update_user_location(user, address: str) -> Dict:
        """
        Обновить местоположение пользователя по адресу
        """
        from back.models.geolocation_models import UserLocation

        dgis = DGisService()
        geocode_result = dgis.geocode_address(address)

        if not geocode_result:
            raise HttpError(400, "Не удалось определить координаты по адресу")

        user_location, created = UserLocation.objects.get_or_create(user=user)
        user_location.latitude = geocode_result['latitude']
        user_location.longitude = geocode_result['longitude']
        user_location.address = geocode_result['full_address']

        # Определяем город из адреса
        address_parts = geocode_result['full_address'].split(',')
        user_location.city = address_parts[0].strip() if len(address_parts) > 0 else ""

        user_location.save()

        return {
            'success': True,
            'coordinates': {
                'lat': geocode_result['latitude'],
                'lon': geocode_result['longitude']
            },
            'address': geocode_result['full_address']
        }

    @staticmethod
    def get_user_location(user) -> Dict:
        """
        Получить местоположение пользователя
        """
        from back.models.geolocation_models import UserLocation

        try:
            user_location = UserLocation.objects.get(user=user)
            return {
                'exists': True,
                'location': {
                    'latitude': user_location.latitude,
                    'longitude': user_location.longitude,
                    'address': user_location.address,
                    'city': user_location.city
                }
            }
        except UserLocation.DoesNotExist:
            return {
                'exists': False,
                'location': None
            }

    @staticmethod
    def find_nearby_workers(customer_lat: float, customer_lon: float, max_distance_km: int = 10) -> List[Dict]:
        """
        Найти работников поблизости от клиента
        """
        from back.models.geolocation_models import UserLocation

        # Получаем всех работников с указанными локациями
        workers_with_locations = UserLocation.objects.filter(
            user__worker_profile__isnull=False,
            latitude__isnull=False,
            longitude__isnull=False
        ).select_related('user', 'user__worker_profile')

        dgis = DGisService()
        origins = [(customer_lat, customer_lon)]
        destinations = [(loc.latitude, loc.longitude) for loc in workers_with_locations]

        if not destinations:
            return []

        # Рассчитываем расстояния
        distance_matrix = dgis.calculate_distance_matrix(origins, destinations)

        nearby_workers = []
        for i, worker_location in enumerate(workers_with_locations):
            distance = distance_matrix[0][i] if distance_matrix and i in distance_matrix.get(0, {}) else None

            if distance and distance <= max_distance_km:
                worker = worker_location.user
                nearby_workers.append({
                    'worker_id': worker.id,
                    'username': worker.username,
                    'specialization': worker.worker_profile.specialization,
                    'rating': worker.worker_profile.rating,
                    'distance_km': distance,
                    'address': worker_location.address
                })

        # Сортируем по расстоянию
        nearby_workers.sort(key=lambda x: x['distance_km'])
        return nearby_workers

    @staticmethod
    def search_nearby_parts_shops(lat: float, lon: float, part_name: str = "запчасти") -> List[Dict]:
        """
        Найти магазины запчастей поблизости
        """
        dgis = DGisService()
        query = f"{part_name} бытовая техника"
        return dgis.search_businesses(query, lat, lon, radius=5000)