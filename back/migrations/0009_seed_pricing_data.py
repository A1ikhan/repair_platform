from django.db import migrations

BASE_PRICES = {
    'fridge':         20_000,
    'washer':         15_000,
    'dryer':          14_000,
    'oven':           10_000,
    'microwave':       8_000,
    'dishwasher':     14_000,
    'tv':             15_000,
    'ac':             22_000,
    'water_heater':   14_000,
    'vacuum':          6_000,
    'coffee_machine': 11_000,
    'other':          10_000,
}

# (device_type, phrase, price_multiplier, confidence_boost, repair_type)
KEYWORDS = [
    # ── fridge ──────────────────────────────────────────────────────────────
    ('fridge', 'электронный модуль', 2.8, 0.15, 'major'),
    ('fridge', 'утечка фреона',      2.0, 0.15, 'major'),
    ('fridge', 'компрессор',         2.5, 0.15, 'major'),
    ('fridge', 'испаритель',         2.2, 0.12, 'major'),
    ('fridge', 'конденсатор',        2.0, 0.12, 'major'),
    ('fridge', 'плата управления',   2.5, 0.12, 'major'),
    ('fridge', 'мотор',              2.0, 0.12, 'major'),
    ('fridge', 'фреон',              1.8, 0.12, 'major'),
    ('fridge', 'плата',              2.3, 0.10, 'major'),
    ('fridge', 'не охлаждает',       1.3, 0.10, 'medium'),
    ('fridge', 'не морозит',         1.3, 0.10, 'medium'),
    ('fridge', 'не включается',      1.2, 0.08, 'medium'),
    ('fridge', 'намерзает',          1.2, 0.08, 'medium'),
    ('fridge', 'термостат',          1.1, 0.10, 'medium'),
    ('fridge', 'вентилятор',         1.1, 0.10, 'medium'),
    ('fridge', 'течет',              1.1, 0.08, 'medium'),
    ('fridge', 'шумит',              1.0, 0.05, 'medium'),
    ('fridge', 'вибрирует',          1.0, 0.05, 'medium'),
    ('fridge', 'запах',              0.9, 0.05, 'medium'),
    ('fridge', 'лёд',                1.0, 0.05, 'medium'),
    ('fridge', 'уплотнитель',        0.55, 0.12, 'simple'),
    ('fridge', 'дверца',             0.45, 0.10, 'simple'),
    ('fridge', 'лампочка',           0.30, 0.15, 'simple'),
    ('fridge', 'свет',               0.35, 0.08, 'simple'),
    ('fridge', 'полка',              0.30, 0.12, 'simple'),
    ('fridge', 'ручка',              0.30, 0.12, 'simple'),
    ('fridge', 'кнопка',             0.40, 0.10, 'simple'),
    # ── washer ──────────────────────────────────────────────────────────────
    ('washer', 'электронный модуль', 2.8, 0.15, 'major'),
    ('washer', 'подшипник',          2.2, 0.15, 'major'),
    ('washer', 'барабан',            2.5, 0.12, 'major'),
    ('washer', 'мотор',              2.5, 0.12, 'major'),
    ('washer', 'плата управления',   2.5, 0.12, 'major'),
    ('washer', 'плата',              2.3, 0.10, 'major'),
    ('washer', 'нагревательный элемент', 0.85, 0.12, 'medium'),
    ('washer', 'не отжимает',        0.90, 0.10, 'medium'),
    ('washer', 'не нагревает',       0.80, 0.10, 'medium'),
    ('washer', 'не сливает',         0.70, 0.10, 'medium'),
    ('washer', 'не включается',      0.75, 0.08, 'medium'),
    ('washer', 'тэн',                0.85, 0.12, 'medium'),
    ('washer', 'помпа',              0.80, 0.12, 'medium'),
    ('washer', 'насос',              0.75, 0.10, 'medium'),
    ('washer', 'щетки',              0.75, 0.12, 'medium'),
    ('washer', 'течет',              0.70, 0.08, 'medium'),
    ('washer', 'вибрирует',          0.90, 0.08, 'medium'),
    ('washer', 'шумит',              0.75, 0.05, 'medium'),
    ('washer', 'уплотнитель',        0.45, 0.10, 'simple'),
    ('washer', 'засор',              0.30, 0.12, 'simple'),
    ('washer', 'фильтр',             0.25, 0.12, 'simple'),
    ('washer', 'шланг',              0.35, 0.12, 'simple'),
    ('washer', 'ручка',              0.25, 0.12, 'simple'),
    # ── oven ────────────────────────────────────────────────────────────────
    ('oven', 'электронный модуль', 2.5, 0.15, 'major'),
    ('oven', 'плата',              2.3, 0.12, 'major'),
    ('oven', 'тэн',                1.7, 0.12, 'major'),
    ('oven', 'нагревательный элемент', 1.7, 0.12, 'major'),
    ('oven', 'не нагревает',       1.5, 0.10, 'medium'),
    ('oven', 'не включается',      1.4, 0.08, 'medium'),
    ('oven', 'термостат',          1.5, 0.10, 'medium'),
    ('oven', 'горелка',            1.4, 0.10, 'medium'),
    ('oven', 'не зажигается',      1.3, 0.10, 'medium'),
    ('oven', 'запах',              1.2, 0.05, 'medium'),
    ('oven', 'ручка',              0.5, 0.12, 'simple'),
    ('oven', 'дверца',             0.7, 0.10, 'simple'),
    ('oven', 'уплотнитель',        0.8, 0.12, 'simple'),
    ('oven', 'лампочка',           0.4, 0.15, 'simple'),
    ('oven', 'кнопка',             0.6, 0.10, 'simple'),
    # ── dishwasher ──────────────────────────────────────────────────────────
    ('dishwasher', 'электронный модуль', 2.8, 0.15, 'major'),
    ('dishwasher', 'насос',              1.8, 0.12, 'major'),
    ('dishwasher', 'помпа',              1.8, 0.12, 'major'),
    ('dishwasher', 'плата',              2.5, 0.12, 'major'),
    ('dishwasher', 'не моет',            1.4, 0.10, 'medium'),
    ('dishwasher', 'не сливает',         1.3, 0.10, 'medium'),
    ('dishwasher', 'течет',              1.4, 0.08, 'medium'),
    ('dishwasher', 'не нагревает',       1.5, 0.10, 'medium'),
    ('dishwasher', 'тэн',                1.5, 0.12, 'medium'),
    ('dishwasher', 'не включается',      1.3, 0.08, 'medium'),
    ('dishwasher', 'шумит',              1.2, 0.05, 'medium'),
    ('dishwasher', 'засор',              0.8, 0.12, 'simple'),
    ('dishwasher', 'фильтр',             0.6, 0.12, 'simple'),
    ('dishwasher', 'уплотнитель',        0.8, 0.10, 'simple'),
    ('dishwasher', 'ручка',              0.5, 0.12, 'simple'),
    # ── microwave ───────────────────────────────────────────────────────────
    ('microwave', 'магнетрон',      2.5, 0.15, 'major'),
    ('microwave', 'трансформатор',  2.2, 0.15, 'major'),
    ('microwave', 'плата',          2.0, 0.12, 'major'),
    ('microwave', 'не греет',       1.5, 0.10, 'medium'),
    ('microwave', 'не включается',  1.3, 0.08, 'medium'),
    ('microwave', 'искрит',         1.4, 0.10, 'medium'),
    ('microwave', 'шумит',          1.2, 0.05, 'medium'),
    ('microwave', 'поворотный стол',0.5, 0.12, 'simple'),
    ('microwave', 'дверца',         0.7, 0.10, 'simple'),
    ('microwave', 'лампочка',       0.4, 0.15, 'simple'),
    ('microwave', 'кнопка',         0.6, 0.10, 'simple'),
    # ── tv ──────────────────────────────────────────────────────────────────
    ('tv', 'матрица',        3.0, 0.15, 'major'),
    ('tv', 'подсветка',      2.5, 0.15, 'major'),
    ('tv', 'плата',          2.3, 0.12, 'major'),
    ('tv', 'блок питания',   2.0, 0.12, 'major'),
    ('tv', 'не включается',  1.4, 0.08, 'medium'),
    ('tv', 'нет изображения',1.5, 0.10, 'medium'),
    ('tv', 'нет звука',      1.3, 0.10, 'medium'),
    ('tv', 'полосы',         1.5, 0.10, 'medium'),
    ('tv', 'мигает',         1.3, 0.08, 'medium'),
    ('tv', 'пульт',          0.3, 0.15, 'simple'),
    ('tv', 'кнопка',         0.5, 0.10, 'simple'),
    # ── ac ──────────────────────────────────────────────────────────────────
    ('ac', 'компрессор',    2.8, 0.15, 'major'),
    ('ac', 'фреон',         1.8, 0.12, 'major'),
    ('ac', 'утечка фреона', 2.0, 0.15, 'major'),
    ('ac', 'плата',         2.3, 0.12, 'major'),
    ('ac', 'не охлаждает',  1.5, 0.10, 'medium'),
    ('ac', 'не греет',      1.5, 0.10, 'medium'),
    ('ac', 'течет',         1.3, 0.08, 'medium'),
    ('ac', 'не включается', 1.3, 0.08, 'medium'),
    ('ac', 'шумит',         1.2, 0.05, 'medium'),
    ('ac', 'фильтр',        0.5, 0.12, 'simple'),
    ('ac', 'пульт',         0.3, 0.15, 'simple'),
    # ── water_heater ────────────────────────────────────────────────────────
    ('water_heater', 'тэн',        1.7, 0.12, 'major'),
    ('water_heater', 'термостат',  1.5, 0.12, 'major'),
    ('water_heater', 'плата',      2.0, 0.12, 'major'),
    ('water_heater', 'течет',      1.4, 0.10, 'medium'),
    ('water_heater', 'не нагревает',1.5, 0.10, 'medium'),
    ('water_heater', 'не включается',1.3, 0.08, 'medium'),
    ('water_heater', 'запах',      1.2, 0.05, 'medium'),
    ('water_heater', 'анод',       0.7, 0.12, 'simple'),
    ('water_heater', 'клапан',     0.8, 0.10, 'simple'),
    ('water_heater', 'шланг',      0.6, 0.10, 'simple'),
    # ── vacuum ──────────────────────────────────────────────────────────────
    ('vacuum', 'мотор',        2.0, 0.15, 'major'),
    ('vacuum', 'не всасывает', 1.3, 0.10, 'medium'),
    ('vacuum', 'не включается',1.3, 0.08, 'medium'),
    ('vacuum', 'шумит',        1.2, 0.05, 'medium'),
    ('vacuum', 'засор',        0.6, 0.15, 'simple'),
    ('vacuum', 'шланг',        0.7, 0.12, 'simple'),
    ('vacuum', 'фильтр',       0.5, 0.12, 'simple'),
    ('vacuum', 'щетка',        0.6, 0.10, 'simple'),
    # ── dryer ───────────────────────────────────────────────────────────────
    ('dryer', 'тэн',          1.8, 0.12, 'major'),
    ('dryer', 'мотор',        2.2, 0.12, 'major'),
    ('dryer', 'плата',        2.3, 0.12, 'major'),
    ('dryer', 'не сушит',     1.5, 0.10, 'medium'),
    ('dryer', 'не греет',     1.5, 0.10, 'medium'),
    ('dryer', 'не включается',1.3, 0.08, 'medium'),
    ('dryer', 'шумит',        1.2, 0.05, 'medium'),
    ('dryer', 'фильтр',       0.5, 0.12, 'simple'),
    ('dryer', 'ручка',        0.5, 0.12, 'simple'),
    ('dryer', 'уплотнитель',  0.8, 0.10, 'simple'),
    # ── coffee_machine ──────────────────────────────────────────────────────
    ('coffee_machine', 'помпа',        2.0, 0.12, 'major'),
    ('coffee_machine', 'бойлер',       2.2, 0.15, 'major'),
    ('coffee_machine', 'плата',        2.3, 0.12, 'major'),
    ('coffee_machine', 'не варит',     1.4, 0.10, 'medium'),
    ('coffee_machine', 'не нагревает', 1.4, 0.10, 'medium'),
    ('coffee_machine', 'течет',        1.3, 0.08, 'medium'),
    ('coffee_machine', 'не включается',1.3, 0.08, 'medium'),
    ('coffee_machine', 'засор',        0.7, 0.12, 'simple'),
    ('coffee_machine', 'клапан',       0.8, 0.10, 'simple'),
    ('coffee_machine', 'уплотнитель',  0.7, 0.10, 'simple'),
    # ── generic (all devices) ───────────────────────────────────────────────
    ('__generic__', 'электронный модуль', 2.5, 0.12, 'major'),
    ('__generic__', 'плата управления',   2.3, 0.12, 'major'),
    ('__generic__', 'мотор',              2.0, 0.10, 'major'),
    ('__generic__', 'плата',              2.0, 0.10, 'major'),
    ('__generic__', 'не включается',      1.3, 0.08, 'medium'),
    ('__generic__', 'течет',              1.3, 0.08, 'medium'),
    ('__generic__', 'шумит',              1.1, 0.05, 'medium'),
    ('__generic__', 'запах',              1.1, 0.05, 'medium'),
    ('__generic__', 'ручка',              0.5, 0.10, 'simple'),
    ('__generic__', 'кнопка',             0.6, 0.10, 'simple'),
    ('__generic__', 'лампочка',           0.4, 0.12, 'simple'),
]


def seed_pricing(apps, schema_editor):
    DeviceBasePrice = apps.get_model('back', 'DeviceBasePrice')
    RepairKeyword = apps.get_model('back', 'RepairKeyword')

    for device_type, price in BASE_PRICES.items():
        DeviceBasePrice.objects.get_or_create(
            device_type=device_type,
            defaults={'base_price': price},
        )

    for device_type, phrase, multiplier, boost, repair_type in KEYWORDS:
        RepairKeyword.objects.get_or_create(
            device_type=device_type,
            phrase=phrase,
            defaults={
                'price_multiplier': multiplier,
                'confidence_boost': boost,
                'repair_type': repair_type,
                'is_active': True,
            },
        )


def unseed_pricing(apps, schema_editor):
    apps.get_model('back', 'DeviceBasePrice').objects.all().delete()
    apps.get_model('back', 'RepairKeyword').objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0008_pricing_models'),
    ]

    operations = [
        migrations.RunPython(seed_pricing, unseed_pricing),
    ]
