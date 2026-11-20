from django.contrib import admin

from .models import Branch, Business


class BranchInline(admin.TabularInline):
    model = Branch
    extra = 0


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "legal_name", "currency", "is_active")
    inlines = [BranchInline]


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "is_active")
    list_filter = ("business", "is_active")
