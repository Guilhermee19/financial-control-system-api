from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *

admin.site.site_header = "ControlFinance - Admin"

admin.site.unregister(Group)
# admin.site.unregister(User)

admin.site.register(Tag)
admin.site.register(Conta)
admin.site.register(Finance)
# admin.site.register(Parcela)
# admin.site.register(FinanceEntry)