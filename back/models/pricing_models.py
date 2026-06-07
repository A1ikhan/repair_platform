from django.db import models

DEVICE_TYPE_CHOICES = [
    ('fridge',        'Холодильник'),
    ('washer',        'Стиральная машина'),
    ('dryer',         'Сушилка'),
    ('oven',          'Духовка / плита'),
    ('microwave',     'Микроволновка'),
    ('dishwasher',    'Посудомоечная машина'),
    ('tv',            'Телевизор'),
    ('ac',            'Кондиционер'),
    ('water_heater',  'Водонагреватель'),
    ('vacuum',        'Пылесос'),
    ('coffee_machine','Кофемашина'),
    ('other',         'Другое'),
    ('__generic__',   'Все устройства (общие слова)'),
]

REPAIR_TYPE_CHOICES = [
    ('simple', 'Простой'),
    ('medium', 'Средний'),
    ('major',  'Сложный'),
]


class DeviceBasePrice(models.Model):
    device_type = models.CharField(
        'Тип устройства', max_length=30, choices=DEVICE_TYPE_CHOICES, unique=True
    )
    base_price = models.PositiveIntegerField('Базовая цена (₸)')

    class Meta:
        verbose_name = 'Базовая цена устройства'
        verbose_name_plural = 'Базовые цены устройств'
        ordering = ['device_type']

    def __str__(self):
        return f'{self.get_device_type_display()} — {self.base_price:,} ₸'


class RepairKeyword(models.Model):
    device_type = models.CharField(
        'Тип устройства', max_length=30, choices=DEVICE_TYPE_CHOICES, db_index=True
    )
    phrase = models.CharField('Ключевая фраза', max_length=100)
    price_multiplier = models.FloatField('Множитель цены')
    confidence_boost = models.FloatField('Прирост уверенности')
    repair_type = models.CharField('Тип ремонта', max_length=10, choices=REPAIR_TYPE_CHOICES)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Ключевое слово ремонта'
        verbose_name_plural = 'Ключевые слова ремонта'
        unique_together = ['device_type', 'phrase']
        ordering = ['device_type', 'repair_type', '-price_multiplier']

    def __str__(self):
        return f'[{self.get_device_type_display()}] {self.phrase} ×{self.price_multiplier}'
