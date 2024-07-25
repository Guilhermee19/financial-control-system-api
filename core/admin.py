from django.contrib import admin
from .models import *

# Register your models here.

admin.site.site_header = "ControlFinance - Admin"

admin.site.register(Tag)
# admin.site.register(Conta)
# admin.site.register(Finance)
# admin.site.register(Parcela)
# admin.site.register(FinanceEntry)