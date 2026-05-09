from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0005_add_db_constraints'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repairrequest',
            name='device_type',
            field=models.CharField(
                max_length=50,
                choices=[
                    ('fridge', 'Refrigerator'),
                    ('washer', 'Washing Machine'),
                    ('dryer', 'Dryer'),
                    ('oven', 'Oven'),
                    ('microwave', 'Microwave'),
                    ('dishwasher', 'Dishwasher'),
                    ('tv', 'Television'),
                    ('ac', 'Air Conditioner'),
                    ('water_heater', 'Water Heater'),
                    ('vacuum', 'Vacuum Cleaner'),
                    ('coffee_machine', 'Coffee Machine'),
                    ('other', 'Other'),
                ],
            ),
        ),
    ]
