# Generated by Django 4.2.1 on 2024-07-25 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='bg_color',
            field=models.CharField(default='#f0f2f8', max_length=20),
        ),
    ]
