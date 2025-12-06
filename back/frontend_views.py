from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def index(request):
    """Главная страница"""
    return render(request, 'index.html')

@ensure_csrf_cookie
def login_view(request):
    """Страница входа"""
    return render(request, 'auth/login.html')

@ensure_csrf_cookie
def register_view(request):
    """Страница регистрации"""
    return render(request, 'auth/register.html')

@ensure_csrf_cookie
def repairs_list_view(request):
    """Все заявки"""
    return render(request, 'repairs/list.html')

@ensure_csrf_cookie
def my_repairs_view(request):
    """Мои заявки"""
    return render(request, 'repairs/my.html')

@ensure_csrf_cookie
def create_repair_view(request):
    """Создание заявки"""
    return render(request, 'repairs/create.html')

@ensure_csrf_cookie
def profile_view(request):
    """Профиль пользователя"""
    return render(request, 'profile/index.html')