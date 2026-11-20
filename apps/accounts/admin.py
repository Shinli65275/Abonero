from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import EmployeeProfile, User


class EmployeeProfileInline(admin.StackedInline):
    model = EmployeeProfile
    can_delete = False


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    inlines = [EmployeeProfileInline]
    list_display = ("username", "get_full_name", "role", "business", "is_active")
    list_filter = ("role", "is_active", "business")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Datos personales", {"fields": ("first_name", "last_name", "email")}),
        ("Empresa y rol", {"fields": ("business", "role")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2", "business", "role", "first_name", "last_name"),
        }),
    )
