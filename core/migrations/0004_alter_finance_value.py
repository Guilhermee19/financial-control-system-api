# Generated by Django 4.2.1 on 2024-08-22 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_finance_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finance',
            name='value',
            field=models.FloatField(),
        ),
    ]