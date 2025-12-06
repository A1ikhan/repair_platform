# check_paths.py
import os
import sys

# Добавим путь к проекту
project_path = '/home/esengaliev/PycharmProjects/repair-platform'
sys.path.insert(0, project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.conf import settings
from pathlib import Path

print("=" * 50)
print("Проверка путей Django")
print("=" * 50)

print(f"\n1. BASE_DIR: {settings.BASE_DIR}")
print(f"   Существует: {os.path.exists(settings.BASE_DIR)}")

print(f"\n2. Ожидаемый путь к templates: {settings.BASE_DIR / 'templates'}")
print(f"   Существует: {os.path.exists(settings.BASE_DIR / 'templates')}")

if os.path.exists(settings.BASE_DIR / 'templates'):
    print(f"   Файлы в templates: {os.listdir(settings.BASE_DIR / 'templates')}")

print(f"\n3. Ожидаемый путь к index.html: {settings.BASE_DIR / 'templates' / 'index.html'}")
print(f"   Существует: {os.path.exists(settings.BASE_DIR / 'templates' / 'index.html')}")

print(f"\n4. DIRS в TEMPLATES:")
for i, dir_path in enumerate(settings.TEMPLATES[0]['DIRS']):
    print(f"   {i+1}. {dir_path}")
    print(f"      Существует: {os.path.exists(dir_path)}")

print(f"\n5. Текущая рабочая директория: {os.getcwd()}")
print("=" * 50)