from ninja import NinjaAPI
from back.dependencies import AuthBearer

# Импортируем саброутеры
from back.endpoints import auth, repairs, responses, reviews, notification, workers

api = NinjaAPI(
    title="Repair Platform API",
    version="1.0.0",
    description="API for appliance repair service platform",
    auth=AuthBearer(),
    csrf=True,
)

# Подключаем роутеры
api.add_router("/auth", auth.router)
api.add_router("/repairs", repairs.router)
api.add_router("/responses", responses.router)
api.add_router("/reviews", reviews.router)
api.add_router("/notifications", notification.router)
api.add_router("/workers", workers.router)

# Тестовые эндпоинты

# Импортируем саброутеры
from .api import auth, repairs, responses, reviews, notification, workers

api = NinjaAPI(
    title="Repair Platform API",
    version="1.0.0",
    description="API for appliance repair service platform",
    auth=AuthBearer(),
    csrf=True,
)

# Подключаем роутеры
api.add_router("/auth", auth.router)
api.add_router("/repairs", repairs.router)
api.add_router("/responses", responses.router)
api.add_router("/reviews", reviews.router)
api.add_router("/notifications", notification.router)
api.add_router("/workers", workers.router)

@api.get("/protected/test",tags=["test"])
def test_protected(request):
    return {"message": f"Hello {request.user.username}!"}

@api.get("/public/hello", auth=None,tags=["test"])
def hello_public(request):
    return {"message": "Hello from Repair Platform API!"}
from ninja import NinjaAPI
from back.dependencies import AuthBearer
