import io
import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from back.models.users_models import CustomerProfile, WorkerProfile, UserActivity
from back.models.repair_requests_models import RepairRequest, ProblemPhoto, RepairRequestFile
from back.models.response_models import Response
from back.models.reviews_models import Review
from back.models.chat_model import ChatMessage
from back.models.notifications_models import Notification
from back.models.bookmark_models import BookmarkFolder, Bookmark
from back.models.userlist_model import UserList, ListItem
from back.models.geolocation_models import UserLocation, ServiceArea


ALMATY_ADDRESSES = [
    "ул. Абая 10, Алматы",
    "пр. Достык 5, Алматы",
    "ул. Толе би 50, Алматы",
    "мкр. Тастак-2, д.15, Алматы",
    "ул. Байзакова 280, Алматы",
    "пр. Назарбаева 77, Алматы",
    "ул. Сейфуллина 500, Алматы",
    "мкр. Алмагуль, д.3, Алматы",
    "ул. Жандосова 94, Алматы",
    "пр. Аль-Фараби 17, Алматы",
]

SPECIALIZATIONS = [
    "Ремонт холодильников",
    "Ремонт стиральных машин",
    "Ремонт духовых шкафов и плит",
    "Ремонт кондиционеров",
    "Ремонт телевизоров и электроники",
    "Ремонт посудомоечных машин",
    "Ремонт кофемашин",
    "Ремонт мелкой бытовой техники",
    "Ремонт водонагревателей",
    "Универсальный мастер по бытовой технике",
]

REPAIR_DATA = [
    {
        "title": "Не морозит холодильник Samsung",
        "description": "Холодильник Samsung двухкамерный. Верхняя камера перестала морозить, нижняя работает нормально. Компрессор шумит.",
        "device_type": "fridge",
        "predicted_price": Decimal("15000"),
        "price_confidence": 0.72,
    },
    {
        "title": "Стиральная машина не отжимает",
        "description": "LG стиральная машина, автомат, 6 кг. После стирки белье остается мокрым, отжим не работает. Ошибка E6 на дисплее.",
        "device_type": "washer",
        "predicted_price": Decimal("9000"),
        "price_confidence": 0.68,
    },
    {
        "title": "Духовой шкаф не нагревается",
        "description": "Встроенный духовой шкаф Bosch. Нагрев перестал работать 3 дня назад. Гриль работает, а нагрев нет.",
        "device_type": "oven",
        "predicted_price": Decimal("8000"),
        "price_confidence": 0.65,
    },
    {
        "title": "Кондиционер не охлаждает",
        "description": "Сплит-система Daikin, установлена 2 года назад. Гоняет воздух, но не холодит. Возможно нужна заправка фреоном.",
        "device_type": "ac",
        "predicted_price": Decimal("12000"),
        "price_confidence": 0.80,
    },
    {
        "title": "Посудомойка течет снизу",
        "description": "Встроенная посудомоечная машина Electrolux. Замечена лужа под машиной после цикла мытья. Раньше такого не было.",
        "device_type": "dishwasher",
        "predicted_price": Decimal("7000"),
        "price_confidence": 0.60,
    },
    {
        "title": "Телевизор Samsung не включается",
        "description": "Телевизор 55 дюймов, Smart TV. Индикатор мигает красным, изображения нет. Несколько раз ударил током из розетки.",
        "device_type": "tv",
        "predicted_price": Decimal("11000"),
        "price_confidence": 0.55,
    },
    {
        "title": "Холодильник постоянно гудит",
        "description": "Холодильник Indesit издает сильный шум, особенно ночью. Температура держит нормально, но гудит очень громко.",
        "device_type": "fridge",
        "predicted_price": Decimal("6000"),
        "price_confidence": 0.58,
    },
    {
        "title": "Сушилка не сушит",
        "description": "Отдельностоящая сушильная машина Candy. Барабан крутится, нагрев не работает. Белье остается влажным после 2 часов.",
        "device_type": "dryer",
        "predicted_price": Decimal("10000"),
        "price_confidence": 0.70,
    },
    {
        "title": "Микроволновка искрит внутри",
        "description": "Микроволновая печь Panasonic. Во время работы видны искры на потолке камеры. Запах горелого.",
        "device_type": "microwave",
        "predicted_price": Decimal("4000"),
        "price_confidence": 0.75,
    },
    {
        "title": "Водонагреватель не греет воду",
        "description": "Накопительный водонагреватель Ariston 80л. Индикатор включен, но вода холодная. Не грел уже 2 дня.",
        "device_type": "water_heater",
        "predicted_price": Decimal("8500"),
        "price_confidence": 0.67,
    },
    {
        "title": "Кофемашина De'Longhi не готовит",
        "description": "Автоматическая кофемашина. Мигает ошибка, кофе не варит. Воду засыпал, воду залил — не помогает.",
        "device_type": "coffee_machine",
        "predicted_price": Decimal("13000"),
        "price_confidence": 0.62,
    },
    {
        "title": "Пылесос Dyson потерял мощность",
        "description": "Беспроводной пылесос Dyson V11. Заряжается нормально, но всасывание очень слабое. Фильтр чистил.",
        "device_type": "vacuum",
        "predicted_price": Decimal("5000"),
        "price_confidence": 0.71,
    },
    {
        "title": "Холодильник Side-by-Side — вода на полке",
        "description": "Холодильник LG Side-by-Side. Внутри появляется вода, стекает на продукты. Уплотнитель целый.",
        "device_type": "fridge",
        "predicted_price": Decimal("7500"),
        "price_confidence": 0.64,
    },
    {
        "title": "Стиральная машина барабан стучит",
        "description": "Samsung стиральная машина. Во время отжима барабан очень сильно стучит и вибрирует. Возможно слетел подшипник.",
        "device_type": "washer",
        "predicted_price": Decimal("14000"),
        "price_confidence": 0.73,
    },
    {
        "title": "AC не запускается, пульт реагирует",
        "description": "Кондиционер Midea настенный 12000 BTU. Пульт принимает команды (мигает индикатор), но агрегат не включается.",
        "device_type": "ac",
        "predicted_price": Decimal("6500"),
        "price_confidence": 0.66,
    },
    {
        "title": "Посудомойка не сливает воду",
        "description": "Bosch посудомоечная машина встроенная. После цикла вода остается на дне. Ошибка E24.",
        "device_type": "dishwasher",
        "predicted_price": Decimal("6000"),
        "price_confidence": 0.69,
    },
    {
        "title": "Духовка не держит температуру",
        "description": "Газовая духовка Gorenje. Выставляю 180°C, но реальная температура прыгает от 100 до 250°C. Пироги не пропекаются.",
        "device_type": "oven",
        "predicted_price": Decimal("9500"),
        "price_confidence": 0.61,
    },
    {
        "title": "Телевизор LG — черные полосы на экране",
        "description": "LG OLED 65 дюймов, 3 года. Появились вертикальные черные полосы по всему экрану. Был небольшой удар по боку.",
        "device_type": "tv",
        "predicted_price": Decimal("25000"),
        "price_confidence": 0.50,
    },
    {
        "title": "Микроволновка Samsung не греет",
        "description": "Samsung MW. Мотор крутит, таймер работает, но еда остается холодной. Магнетрон сгорел скорее всего.",
        "device_type": "microwave",
        "predicted_price": Decimal("7000"),
        "price_confidence": 0.78,
    },
    {
        "title": "Стиралка набирает воду и останавливается",
        "description": "Candy стиральная машина 5кг. Набирает воду, потом просто стоит и не стирает. Ошибки нет на дисплее.",
        "device_type": "washer",
        "predicted_price": Decimal("8000"),
        "price_confidence": 0.65,
    },
]

RESPONSE_MESSAGES = [
    "Добрый день! Могу приехать на диагностику завтра в удобное время. Стоимость диагностики 1500 тг, входит в стоимость ремонта.",
    "Здравствуйте, данная поломка мне хорошо знакома. Возьмусь за работу. Цена окончательная, запчасти включены.",
    "Здравствуйте! Имею большой опыт ремонта данного типа техники. Готов приехать в день обращения.",
    "Добрый день. Проблема решаема. Могу сделать качественно и быстро. Даю гарантию 3 месяца на все виды работ.",
    "Здравствуйте! Работаю официально, есть все необходимые инструменты и запчасти. Приеду в удобное для вас время.",
    "Приветствую! Ремонтирую технику 8 лет. Ваш случай несложный. Готов сделать быстро и качественно.",
    "Здравствуйте, опыт работы 10 лет. Данная проблема типичная, решается за 1-2 часа. Цена указана с учетом деталей.",
    "Добрый день! Специализируюсь именно на этом типе техники. Готов выехать сегодня после 18:00 или завтра с утра.",
]

CHAT_MESSAGES_CUSTOMER = [
    "Здравствуйте! Когда сможете приехать?",
    "Подходит ли вам завтра в 15:00?",
    "Хорошо, буду ждать вас завтра.",
    "Уточните, пожалуйста, нужно ли освобождать место вокруг техники?",
    "Мастер, как долго займет ремонт примерно?",
    "Спасибо за быстрый ответ!",
    "Можете приехать пораньше, в 12:00?",
    "Все готово, жду вас.",
]

CHAT_MESSAGES_WORKER = [
    "Здравствуйте! Могу приехать завтра в 14:00 — подходит?",
    "Да, завтра в 15:00 буду у вас. Адрес уточните пожалуйста.",
    "Хорошо, буду в назначенное время.",
    "Желательно отодвинуть технику от стены на 50 см для удобного доступа.",
    "Обычно такой ремонт занимает 1-2 часа, иногда дольше если нужны запчасти.",
    "Пожалуйста! До встречи.",
    "В 12:00 не могу, есть другой заказ. Могу в 13:30, устроит?",
    "Уже выехал, буду через 20 минут.",
]

REVIEW_COMMENTS = [
    "Мастер приехал вовремя, всё сделал качественно. Очень доволен работой, рекомендую!",
    "Отличная работа! Быстро, аккуратно и по разумной цене. Обращусь снова если что.",
    "Хороший специалист. Объяснил причину поломки и что сделал. Техника работает отлично.",
    "Пришёл в назначенное время. Ремонт занял час. Всё работает, доволен результатом.",
    "Профессионал своего дела. Нашёл проблему быстро. Цена соответствует качеству.",
    "Рекомендую! Честный мастер — сказал что можно отремонтировать дешевле, не стал накручивать цену.",
    "Отремонтировал быстро. Дал гарантию. Надеюсь техника больше не сломается, но если что — обращусь снова.",
    "Работой доволен. Мастер аккуратный, не намусорил. Техника работает как новая.",
]

FOLDER_NAMES = ["Срочные", "Выгодные заказы", "На этой неделе", "Крупный ремонт", "Постоянные клиенты"]
FOLDER_COLORS = ["#EF4444", "#10B981", "#3B82F6", "#F59E0B", "#8B5CF6"]

CITIES = ["Алматы", "Астана", "Шымкент"]

# (background_dark, background_light, accent)
DEVICE_PALETTE = {
    'fridge':        ((30, 90, 150),  (60, 140, 210), (200, 225, 255)),
    'washer':        ((20, 110, 80),  (40, 170, 120), (200, 245, 225)),
    'dryer':         ((100, 50, 150), (150, 90, 200), (230, 210, 255)),
    'oven':          ((160, 60, 10),  (220, 100, 30), (255, 220, 180)),
    'microwave':     ((140, 30, 30),  (200, 60, 60),  (255, 200, 200)),
    'dishwasher':    ((15, 120, 130), (30, 180, 190), (190, 240, 245)),
    'tv':            ((25, 40, 70),   (50, 80, 130),  (180, 200, 240)),
    'ac':            ((30, 100, 170), (60, 150, 220), (200, 230, 255)),
    'water_heater':  ((170, 90, 10),  (220, 140, 30), (255, 230, 180)),
    'vacuum':        ((80, 80, 90),   (130, 130, 145),(220, 220, 230)),
    'coffee_machine':((70, 40, 15),   (120, 75, 35),  (220, 190, 150)),
    'other':         ((60, 70, 80),   (100, 115, 130),(210, 215, 225)),
}

DEVICE_LABELS = {
    'fridge': 'ХОЛОДИЛЬНИК', 'washer': 'СТИРАЛЬНАЯ\nМАШИНА',
    'dryer': 'СУШИЛЬНАЯ\nМАШИНА', 'oven': 'ДУХОВОЙ\nШКАФ',
    'microwave': 'МИКРОВОЛНОВКА', 'dishwasher': 'ПОСУДОМОЙКА',
    'tv': 'ТЕЛЕВИЗОР', 'ac': 'КОНДИЦИОНЕР',
    'water_heater': 'ВОДОНАГРЕ-\nВАТЕЛЬ', 'vacuum': 'ПЫЛЕСОС',
    'coffee_machine': 'КОФЕМАШИНА', 'other': 'ТЕХНИКА',
}

DAMAGE_LABELS = [
    "НЕ РАБОТАЕТ", "НЕИСПРАВНОСТЬ", "ТРЕБУЕТ\nРЕМОНТА",
    "ПОЛОМКА", "НЕИСПРАВЕН", "ОШИБКА",
]


class Command(BaseCommand):
    help = "Seed the database with realistic sample data"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Clear existing seeded data before seeding")

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_data()

        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR("No users found. Create users first."))
            return

        customers, workers = self._assign_profiles(users)
        self.stdout.write(f"  {len(customers)} customers, {len(workers)} workers")

        if not customers or not workers:
            self.stdout.write(self.style.ERROR("Need at least 1 customer and 1 worker to seed data."))
            return

        self._seed_geo(workers, customers)
        requests = self._seed_repair_requests(customers)
        self._seed_responses_and_lifecycle(requests, workers, customers)
        self._seed_userlists(customers, requests)
        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

    def _clear_data(self):
        self.stdout.write("Clearing previous seed data...")
        Bookmark.objects.all().delete()
        BookmarkFolder.objects.all().delete()
        ListItem.objects.all().delete()
        UserList.objects.all().delete()
        Notification.objects.all().delete()
        ChatMessage.objects.all().delete()
        Review.objects.all().delete()
        Response.objects.all().delete()
        RepairRequestFile.objects.all().delete()
        ProblemPhoto.objects.all().delete()
        RepairRequest.objects.all().delete()
        UserActivity.objects.all().delete()
        try:
            UserLocation.objects.all().delete()
            ServiceArea.objects.all().delete()
        except Exception:
            pass
        self.stdout.write("  Cleared.")

    def _assign_profiles(self, users):
        customers, workers = [], []
        for user in users:
            has_customer = hasattr(user, "customer_profile")
            has_worker = hasattr(user, "worker_profile")
            if has_customer:
                customers.append(user)
            elif has_worker:
                workers.append(user)
            else:
                # Assign roles to users without profiles: 60% customer, 40% worker
                if len(customers) * 10 < (len(customers) + len(workers) + 1) * 6:
                    CustomerProfile.objects.get_or_create(user=user)
                    customers.append(user)
                else:
                    wp, _ = WorkerProfile.objects.get_or_create(user=user)
                    if not wp.specialization:
                        wp.specialization = random.choice(SPECIALIZATIONS)
                        wp.experience = random.randint(1, 12)
                        wp.rating = round(random.uniform(3.5, 5.0), 1)
                        wp.is_verified = random.choice([True, True, False])
                        wp.phone_number = f"+7701{random.randint(1000000, 9999999)}"
                        wp.bio = f"Опыт работы {wp.experience} лет. {wp.specialization}."
                        wp.save()
                    workers.append(user)

        # Fill worker profiles for existing workers that lack data
        for w in workers:
            wp = w.worker_profile
            if not wp.specialization:
                wp.specialization = random.choice(SPECIALIZATIONS)
                wp.experience = random.randint(1, 12)
                wp.rating = round(random.uniform(3.5, 5.0), 1)
                wp.is_verified = random.choice([True, True, False])
                wp.phone_number = f"+7701{random.randint(1000000, 9999999)}"
                wp.bio = f"Опыт работы {wp.experience} лет. {wp.specialization}."
                wp.save()

        return customers, workers

    def _seed_geo(self, workers, customers):
        try:
            from django.db import connection
            tables = connection.introspection.table_names()
            if "back_userlocation" not in tables:
                self.stdout.write("  Skipping geolocation (tables not migrated).")
                return
        except Exception:
            return
        self.stdout.write("Seeding geolocation...")
        for user in workers + customers:
            if not UserLocation.objects.filter(user=user).exists():
                addr = random.choice(ALMATY_ADDRESSES)
                UserLocation.objects.create(
                    user=user,
                    latitude=43.2 + random.uniform(-0.1, 0.1),
                    longitude=76.9 + random.uniform(-0.1, 0.1),
                    address=addr,
                    city="Алматы",
                )
        for worker in workers:
            if not ServiceArea.objects.filter(user=worker).exists():
                ServiceArea.objects.create(
                    user=worker,
                    city=random.choice(CITIES),
                    radius_km=random.randint(5, 20),
                )

    def _seed_repair_requests(self, customers):
        self.stdout.write("Seeding repair requests...")
        requests = []
        today = date.today()

        data_pool = REPAIR_DATA * 2  # allow repeats if more customers than scenarios
        random.shuffle(data_pool)

        for i, customer in enumerate(customers):
            count = random.randint(1, 3)
            for j in range(count):
                d = data_pool[(i * 3 + j) % len(data_pool)]
                days_ago = random.randint(1, 60)
                rr = RepairRequest.objects.create(
                    title=d["title"],
                    description=d["description"],
                    device_type=d["device_type"],
                    address=random.choice(ALMATY_ADDRESSES),
                    latitude=43.2 + random.uniform(-0.1, 0.1),
                    longitude=76.9 + random.uniform(-0.1, 0.1),
                    desired_completion_date=today + timedelta(days=random.randint(3, 14)),
                    status="new",
                    created_by=customer,
                    predicted_price=d["predicted_price"],
                    price_confidence=d["price_confidence"],
                )
                self._seed_photos(rr)
                requests.append(rr)
                UserActivity.objects.create(
                    user=customer,
                    activity_type="request_create",
                    description=f"Создана заявка: {rr.title}",
                    target_model="RepairRequest",
                    target_id=rr.id,
                )
        self.stdout.write(f"  Created {len(requests)} repair requests.")
        return requests

    def _seed_responses_and_lifecycle(self, requests, workers, customers):
        self.stdout.write("Seeding responses, chats, reviews, notifications, bookmarks...")
        random.shuffle(requests)

        completed_count = max(1, len(requests) // 4)
        active_count = max(1, len(requests) // 3)
        # First slice: completed, second: active, rest: new
        completed_requests = requests[:completed_count]
        active_requests = requests[completed_count:completed_count + active_count]
        new_requests = requests[completed_count + active_count:]

        all_bookmark_candidates = []

        for rr in requests:
            num_workers = random.randint(1, min(3, len(workers)))
            responding_workers = random.sample(workers, num_workers)
            created_responses = []

            for worker in responding_workers:
                msg = random.choice(RESPONSE_MESSAGES)
                base_price = rr.predicted_price or Decimal("8000")
                price = base_price * Decimal(str(round(random.uniform(0.8, 1.3), 2)))
                price = price.quantize(Decimal("1"))
                resp = Response.objects.create(
                    repair_request=rr,
                    worker=worker,
                    message=msg,
                    proposed_price=price,
                    status="sent",
                )
                created_responses.append(resp)
                UserActivity.objects.create(
                    user=worker,
                    activity_type="response_create",
                    description=f"Отклик на заявку: {rr.title}",
                    target_model="Response",
                    target_id=resp.id,
                )
                Notification.objects.create(
                    user=rr.created_by,
                    message=f"Новый отклик от мастера {worker.get_full_name() or worker.username} на вашу заявку «{rr.title}»",
                    notification_type="new_response",
                )
                all_bookmark_candidates.append((worker, resp))

            if created_responses and rr in (completed_requests + active_requests):
                accepted_resp = random.choice(created_responses)
                accepted_resp.status = "accepted"
                accepted_resp.save()
                for r in created_responses:
                    if r != accepted_resp:
                        r.status = "rejected"
                        r.save()

                rr.status = "active"
                rr.save()

                UserActivity.objects.create(
                    user=rr.created_by,
                    activity_type="response_accept",
                    description=f"Принят отклик для заявки: {rr.title}",
                    target_model="Response",
                    target_id=accepted_resp.id,
                )
                Notification.objects.create(
                    user=accepted_resp.worker,
                    message=f"Ваш отклик принят! Заявка «{rr.title}»",
                    notification_type="response_accepted",
                )

                self._seed_chat(rr, rr.created_by, accepted_resp.worker)

                if rr in completed_requests:
                    final = accepted_resp.proposed_price * Decimal(str(round(random.uniform(0.95, 1.05), 2)))
                    final = final.quantize(Decimal("1"))
                    rr.status = "completed"
                    rr.final_price = final
                    rr.save()

                    self._seed_review(rr, rr.created_by, accepted_resp.worker)

        self._seed_bookmarks(workers, all_bookmark_candidates)

    def _seed_chat(self, rr, customer, worker):
        num_exchanges = random.randint(2, 5)
        for i in range(num_exchanges):
            ChatMessage.objects.create(
                repair_request=rr,
                sender=customer,
                message=random.choice(CHAT_MESSAGES_CUSTOMER),
                is_read=True,
            )
            ChatMessage.objects.create(
                repair_request=rr,
                sender=worker,
                message=random.choice(CHAT_MESSAGES_WORKER),
                is_read=random.choice([True, False]),
            )

    def _seed_review(self, rr, customer, worker):
        if Review.objects.filter(repair_request=rr).exists():
            return
        rating = random.choices([5, 4, 4, 5, 3], weights=[40, 30, 15, 10, 5])[0]
        Review.objects.create(
            repair_request=rr,
            worker=worker,
            customer=customer,
            rating=rating,
            comment=random.choice(REVIEW_COMMENTS),
        )
        wp = worker.worker_profile
        reviews = Review.objects.filter(worker=worker)
        wp.rating = round(sum(r.rating for r in reviews) / reviews.count(), 2)
        wp.save()
        UserActivity.objects.create(
            user=customer,
            activity_type="review_create",
            description=f"Оставлен отзыв для мастера {worker.username}",
            target_model="Review",
        )
        Notification.objects.create(
            user=worker,
            message=f"Клиент оставил отзыв на вашу работу по заявке «{rr.title}» — {rating}/5",
            notification_type="new_review",
        )

    def _seed_bookmarks(self, workers, candidates):
        for worker in workers:
            worker_responses = [(w, r) for w, r in candidates if w == worker]
            if not worker_responses:
                continue
            # Create 1-2 folders per worker
            folders = []
            num_folders = random.randint(1, 2)
            folder_data = random.sample(
                list(zip(FOLDER_NAMES, FOLDER_COLORS)),
                min(num_folders, len(FOLDER_NAMES))
            )
            for name, color in folder_data:
                folder, _ = BookmarkFolder.objects.get_or_create(
                    user=worker, name=name, defaults={"color": color}
                )
                folders.append(folder)

            # Bookmark up to 3 responses
            to_bookmark = random.sample(worker_responses, min(3, len(worker_responses)))
            for _, resp in to_bookmark:
                if Bookmark.objects.filter(user=worker, response=resp).exists():
                    continue
                priority = random.choice(["low", "medium", "high"])
                deadline_days = random.randint(3, 30)
                Bookmark.objects.create(
                    user=worker,
                    response=resp,
                    folder=random.choice(folders) if folders else None,
                    priority=priority,
                    status=random.choice(["new", "in_progress"]),
                    planned_date=date.today() + timedelta(days=random.randint(1, 10)),
                    deadline=date.today() + timedelta(days=deadline_days),
                    notes=f"Интересный заказ. Цена хорошая.",
                    personal_rating=random.randint(3, 5),
                )

    # ── photo helpers ──────────────────────────────────────────────────────────

    def _generate_photo_bytes(self, device_type: str, shot_index: int) -> bytes:
        """Generate a Pillow image that looks like a repair photo and return JPEG bytes."""
        from PIL import Image, ImageDraw

        W, H = 800, 600
        palette = DEVICE_PALETTE.get(device_type, DEVICE_PALETTE['other'])
        dark, light, accent = palette

        img = Image.new('RGB', (W, H))
        draw = ImageDraw.Draw(img)

        # gradient background
        for y in range(H):
            t = y / H
            r = int(dark[0] + (light[0] - dark[0]) * t)
            g = int(dark[1] + (light[1] - dark[1]) * t)
            b = int(dark[2] + (light[2] - dark[2]) * t)
            draw.line([(0, y), (W, y)], fill=(r, g, b))

        # subtle grid lines (simulate surface texture)
        grid_color = tuple(max(0, c - 20) for c in light)
        for x in range(0, W, 40):
            draw.line([(x, 0), (x, H)], fill=grid_color, width=1)
        for y in range(0, H, 40):
            draw.line([(0, y), (W, y)], fill=grid_color, width=1)

        # central "device body" rectangle
        margin_x, margin_y = 120, 80
        draw.rectangle(
            [(margin_x, margin_y), (W - margin_x, H - margin_y)],
            fill=tuple(min(255, c + 30) for c in light),
            outline=accent,
            width=3,
        )

        # per-shot visual variation: scratches / damage marks
        rng = random.Random(device_type + str(shot_index))
        for _ in range(rng.randint(3, 8)):
            x1 = rng.randint(margin_x + 20, W - margin_x - 20)
            y1 = rng.randint(margin_y + 20, H - margin_y - 20)
            x2 = x1 + rng.randint(-60, 60)
            y2 = y1 + rng.randint(-30, 30)
            draw.line([(x1, y1), (x2, y2)], fill=(30, 30, 30), width=rng.randint(1, 3))

        # device label (top-center)
        device_label = DEVICE_LABELS.get(device_type, 'ТЕХНИКА')
        self._draw_centered_text(draw, device_label, W // 2, margin_y + 40,
                                  fill=accent, font_size=28)

        # damage label (bottom-center, red badge)
        damage_text = DAMAGE_LABELS[shot_index % len(DAMAGE_LABELS)]
        badge_y = H - margin_y - 50
        draw.rectangle(
            [(W // 2 - 120, badge_y - 18), (W // 2 + 120, badge_y + 18)],
            fill=(180, 30, 30),
        )
        self._draw_centered_text(draw, damage_text.replace('\n', ' '),
                                  W // 2, badge_y, fill=(255, 255, 255), font_size=18)

        # shot number badge (top-right corner)
        draw.ellipse([(W - 60, 15), (W - 15, 60)], fill=(0, 0, 0, 180))
        self._draw_centered_text(draw, str(shot_index + 1),
                                  W - 37, 37, fill=(255, 255, 255), font_size=18)

        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
        return buf.getvalue()

    @staticmethod
    def _draw_centered_text(draw, text, cx, cy, fill, font_size):
        """Draw text centered at (cx, cy). Falls back to default font gracefully."""
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", font_size)
        except (IOError, OSError):
            try:
                from PIL import ImageFont
                font = ImageFont.load_default()
            except Exception:
                font = None

        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        else:
            tw, th = len(text) * 6, 11

        draw.text((cx - tw // 2, cy - th // 2), text, fill=fill, font=font)

    def _seed_photos(self, rr: RepairRequest):
        """Generate 1–3 photos per repair request and attach as ProblemPhoto + RepairRequestFile."""
        num_photos = random.randint(1, 3)
        for i in range(num_photos):
            jpeg_bytes = self._generate_photo_bytes(rr.device_type, i)
            filename = f"{rr.device_type}_req{rr.id}_shot{i + 1}.jpg"
            content = ContentFile(jpeg_bytes, name=filename)

            # ProblemPhoto (M2M on RepairRequest)
            photo = ProblemPhoto.objects.create(
                uploaded_by=rr.created_by,
                description=f"Фото поломки #{i + 1}",
            )
            photo.image.save(filename, content, save=True)
            rr.problem_photos.add(photo)

            # RepairRequestFile (FK, with thumbnail via ImageKit)
            rrf = RepairRequestFile(
                repair_request=rr,
                uploaded_by=rr.created_by,
                description=f"Фото проблемы #{i + 1}",
                is_public=True,
            )
            rrf.file.save(filename, ContentFile(jpeg_bytes, name=filename), save=True)

    def _seed_userlists(self, customers, requests):
        self.stdout.write("Seeding user lists...")
        list_names = ["favorite", "watching", "applied", "completed"]
        for customer in customers:
            for name in list_names:
                UserList.objects.get_or_create(user=customer, name=name)

            fav_list = UserList.objects.get(user=customer, name="favorite")
            watch_list = UserList.objects.get(user=customer, name="watching")

            other_requests = [r for r in requests if r.created_by != customer]
            if other_requests:
                fav_sample = random.sample(other_requests, min(3, len(other_requests)))
                for rr in fav_sample:
                    ListItem.objects.get_or_create(user_list=fav_list, repair_request=rr)
                    UserActivity.objects.create(
                        user=customer,
                        activity_type="favorite_add",
                        description=f"Добавлено в избранное: {rr.title}",
                        target_model="RepairRequest",
                        target_id=rr.id,
                    )

                watch_sample = random.sample(other_requests, min(2, len(other_requests)))
                for rr in watch_sample:
                    if not ListItem.objects.filter(user_list=watch_list, repair_request=rr).exists():
                        ListItem.objects.get_or_create(user_list=watch_list, repair_request=rr)
