from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

admin.site.site_header = "ControlFinance - Admin"

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'is_admin',)
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email',
                            'password',
                            'profile_image',
                            'name',
                            'is_deleted',
                            'is_active',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',)}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()
    
admin.site.unregister(Group)
# admin.site.unregister(User)

admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Account)
admin.site.register(Card)
admin.site.register(Transaction)