# Generated by Django 5.0.6 on 2024-05-21 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airport_api', '0008_crew_flying_hours'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='accounted',
            field=models.BooleanField(default=False),
        ),
    ]
