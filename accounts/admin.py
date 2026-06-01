from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informazioni Ruolo', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informazioni Ruolo', {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)