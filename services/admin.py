from django.contrib import admin
from .models import Service, AppointmentSlot, Reservation

class AppointmentSlotInline(admin.TabularInline):
    model = AppointmentSlot
    extra = 1
    fields = ('date','start_time','end_time','capacity')
    ordering = ('-date','start_time')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title','deposit_amount_toman','duration_minutes','is_active')
    list_filter = ('is_active',)
    search_fields = ('title','description')
    prepopulated_fields = {'slug':('title',)}
    inlines = [AppointmentSlotInline]

@admin.register(AppointmentSlot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('service','date','start_time','end_time','capacity')
    list_filter = ('service','date')
    search_fields = ('service__title',)
    ordering = ('-date','start_time')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id','user_phone','service','slot_date','time_range','status','amount_toman','zarinpal_ref_id','created_at')
    list_filter = ('status','service','slot__date')
    search_fields = ('id','user__phone_number','zarinpal_ref_id')
    readonly_fields = ('created_at','updated_at','zarinpal_authority','zarinpal_ref_id')
    def user_phone(self, obj): return getattr(obj.user,'phone_number','-')
    user_phone.short_description = 'موبایل'
    def slot_date(self, obj): return obj.slot.date
    slot_date.short_description = 'تاریخ'
    def time_range(self, obj): return f"{obj.slot.start_time.strftime('%H:%M')} تا {obj.slot.end_time.strftime('%H:%M')}"
    time_range.short_description = 'بازه'

