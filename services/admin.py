
from django.contrib import admin
from .models import Categories, Service, Reservation

# 1️⃣ Admin for Categories
@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'slug')  # Fields shown in the list view
    search_fields = ('name',)  # Enable search by category name
    prepopulated_fields = {'slug': ('name',)}  # Auto-generate slug from name

# 2️⃣ Admin for Services
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'active')
    list_filter = ('category', 'active')  # Filter services by category & status
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

# 3️⃣ Admin for Reservations
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service', 'date', 'time', 'created_at')
    list_filter = ('date', 'service')  # Filter by date & service
    search_fields = ('user__username', 'service__name')  # Search by user & service name
    ordering = ('-created_at',)  # Show newest reservations first
