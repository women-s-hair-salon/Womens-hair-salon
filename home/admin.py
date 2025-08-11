from django.contrib import admin

# Register your models here.

# Service
from .models import ServiceCategory, ServiceItem

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {"slug": ("title",)}

@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')


# Contact

from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "created_at")
    search_fields = ("full_name", "email", "message")
