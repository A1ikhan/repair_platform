"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from back.api import api
from back.frontend_views import index, login_view, register_view, repairs_list_view, my_repairs_view, \
    create_repair_view, profile_view, my_responses_view, request_responses_view, logout_view, chat_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),

    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),  # Выход из системы
    path('register/', register_view, name='register'),
    path('repairs/', repairs_list_view, name='repairs_list'),
    path('repairs/my/', my_repairs_view, name='my_repairs'),
    path('repairs/create/', create_repair_view, name='create_repair'),
    path('profile/', profile_view, name='profile'),
    path('responses/my/', my_responses_view, name='my_responses'),
    path('responses/request/<int:request_id>/', request_responses_view, name='request_responses'),
    path('chat/request/<int:request_id>/', chat_view, name='chat'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


