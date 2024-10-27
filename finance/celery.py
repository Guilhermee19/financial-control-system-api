# finance/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Define o ambiente de configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance.settings')

app = Celery('finance')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
