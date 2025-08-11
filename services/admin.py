from django.contrib import admin
from .models import Service, TimeSlot, Reservation

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'deposit', 'duration_minutes')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('service', 'date', 'time')
    list_filter = ('service', 'date')
    search_fields = ('service__name',)
    ordering = ('-date', 'time')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'slot', 'is_paid')
    list_filter = ('is_paid', 'service')
    search_fields = ('user__username', 'user__full_name', 'service__name')
    ordering = ('-slot__date', 'slot__time')
