import requests
from django.contrib import messages
from django.contrib.auth import authenticate,login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def index(request):
    """Главная страница"""
    return render(request, 'index.html')

@ensure_csrf_cookie
def login_view(request):
    """Страница входа"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 1. Проверяем через Django аутентификацию
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 2. Логинимся в Django
            auth_login(request, user)

            # 3. Получаем JWT токены
            try:
                response = requests.post(
                    'http://localhost:8000/api/auth/login',  # или ваш домен
                    json={'username': username, 'password': password},
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code == 200:
                    data = response.json()
                    # Сохраняем JWT в сессии Django для передачи в шаблон
                    request.session['access_token'] = data.get('access')
                    request.session['refresh_token'] = data.get('refresh')

                    messages.success(request, 'Успешный вход!')
                    return redirect('index')
                else:
                    # Если JWT не получен, все равно логинимся в Django
                    messages.warning(request, 'Вход выполнен, но JWT токены не получены')
                    return redirect('index')

            except Exception as e:
                messages.warning(request, f'Вход выполнен, но ошибка JWT: {str(e)}')
                return redirect('index')
        else:
            messages.error(request, 'Неверные учетные данные')

    return render(request, 'auth/login.html')


@ensure_csrf_cookie
def register_view(request):
    """Страница регистрации"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        user_type = request.POST.get('user_type', 'customer')

        try:
            # Регистрируем через API
            response = requests.post(
                'http://localhost:8000/api/auth/register',
                json={
                    'username': username,
                    'email': email,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'user_type': user_type
                },
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
                return redirect('login')
            else:
                data = response.json()
                messages.error(request, data.get('message', 'Ошибка регистрации'))

        except Exception as e:
            messages.error(request, f'Ошибка соединения: {str(e)}')

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

@ensure_csrf_cookie
@login_required
def my_responses_view(request):
    """Мои отклики (для работников)"""
    return render(request, 'responses/my.html')

@ensure_csrf_cookie
@login_required
def request_responses_view(request, request_id):
    """Отклики на конкретную заявку"""
    return render(request, 'responses/request.html', {'request_id': request_id})


def logout_view(request):
    """Выход из системы"""
    # Очищаем сессию Django
    auth_logout(request)

    # Очищаем JWT из сессии
    if 'access_token' in request.session:
        del request.session['access_token']
    if 'refresh_token' in request.session:
        del request.session['refresh_token']

    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('index')

@ensure_csrf_cookie
@login_required
def chat_view(request, request_id):
    """Чат для конкретной заявки"""
    return render(request, 'chat/index.html', {'request_id': request_id})