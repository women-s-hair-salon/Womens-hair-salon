from django.db import models
from django.utils import timezone
from accounts.models import CustomUser

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q

from django.core.validators import MinValueValidator

class Service(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    deposit_amount_toman = models.PositiveIntegerField(validators=[MinValueValidator(10000)])
    duration_minutes = models.PositiveIntegerField(help_text='مدت خدمت (دقیقه)')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['title']

    def __str__(self): return self.title

    def duration_label(self):
        m = self.duration_minutes
        if m < 60: return f"{m} دقیقه"
        h, r = divmod(m, 60)
        return f"{h} ساعت" + (f" و {r} دقیقه" if r else '')


class AppointmentSlotQuerySet(models.QuerySet):
    def future(self):
        return self.filter(date__gte=timezone.localdate())

class AppointmentSlot(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()           # در DB میلادی؛ فرانت جلالی نمایش می‌دهد
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=1)
    is_archived = models.BooleanField(default=False)  # برای نگهداری امن داده‌های گذشته
    objects = AppointmentSlotQuerySet.as_manager()

    class Meta:
        unique_together = ('service','date','start_time','end_time')
        ordering = ['date','start_time']

    def __str__(self): return f"{self.service} — {self.date} {self.start_time}-{self.end_time}"

    def remaining_capacity(self):
        booked = self.reservations.filter(status__in=[Reservation.Status.PENDING, Reservation.Status.BOOKED]).count()
        return max(0, self.capacity - booked)

class Reservation(models.Model):
    class Status(models.TextChoices):
        DRAFT='draft','پیش‌نویس'
        PENDING='pending','در انتظار پرداخت'
        FAILED='failed','ناموفق'
        EXPIRED='expired','منقضی'
        BOOKED='booked','رزروشده'
        CANCELED='canceled','لغو'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='reservations')
    slot = models.ForeignKey(AppointmentSlot, on_delete=models.PROTECT, related_name='reservations')

    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    amount_toman = models.PositiveIntegerField()
    zarinpal_authority = models.CharField(max_length=64, blank=True, null=True)
    zarinpal_ref_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            # اجازه رزروهای متعدد برای یک اسلات، ولی نه برای یک کاربر (که خودت انجام دادی)
            models.UniqueConstraint(
                fields=['slot', 'user'],
                condition=Q(status__in=['pending', 'booked']),
                name='uniq_slot_user_when_active',
            ),
            # Authority فقط وقتی pending/booked و غیرخالی است یونیک باشد
            models.UniqueConstraint(
                fields=['zarinpal_authority'],
                condition=Q(status__in=['pending', 'booked']) &
                          Q(zarinpal_authority__isnull=False) &
                          ~Q(zarinpal_authority=''),
                name='uniq_authority_when_active',
            ),
        ]

    def __str__(self):
        return f"Res#{self.id} {self.user} {self.service} {self.slot} [{self.status}]"

    @transaction.atomic
    def move_to_pending(self):
        # قفل خوش‌رفتار روی ردیف اسلات
        slot = AppointmentSlot.objects.select_for_update().get(pk=self.slot_id)

        # شمار رزروهای فعال همین اسلات
        active_count = Reservation.objects.filter(
            slot=self.slot,
            status__in=[Reservation.Status.PENDING, Reservation.Status.BOOKED]
        ).count()

        if active_count >= slot.capacity:
            raise ValueError('ظرفیت اسلات تکمیل شده است.')

        # اگر همه‌چیز اوکی بود:
        self.status = Reservation.Status.PENDING
        self.save(update_fields=['status', 'updated_at'])

    def time_range_label(self):
        return f"{self.slot.start_time.strftime('%H:%M')} تا {self.slot.end_time.strftime('%H:%M')}"












# services/models.py
from .choices import SERVICE_CHOICES, SERVICE_DURATIONS, SERVICE_DEPOSITS
from django.conf import settings


# class Service(models.Model):
#     name = models.CharField(max_length=200)
#     deposit = models.PositiveIntegerField()
#     duration_minutes = models.PositiveIntegerField()
#
#     def __str__(self):
#         return self.name
#
# # تایم قابل رزرو (ادمین از این بخش تایم‌ها را می‌سازد)
# class TimeSlot(models.Model):
#     service = models.ForeignKey(Service, on_delete=models.CASCADE)
#     date = models.DateField()
#     time = models.TimeField()
#
#     def __str__(self):
#         return f"{self.service.name} - {self.date} {self.time}"
#
# # رزرو کاربر
# class Reservation(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     service = models.ForeignKey(Service, on_delete=models.CASCADE)
#     slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
#     is_paid = models.BooleanField(default=False)
#
#     class Meta:
#         unique_together = ('slot',)

# class Service(models.Model):
#     name = models.CharField(max_length=100)
#     duration_minutes = models.PositiveIntegerField()
#     deposit_amount = models.PositiveIntegerField()
#
# class Reservation(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     service = models.ForeignKey(Service, on_delete=models.CASCADE)
#     start_datetime = models.DateTimeField()
#     end_datetime = models.DateTimeField()
#     is_paid = models.BooleanField(default=False)
#     deposit_amount = models.PositiveIntegerField()
#     zarinpal_transaction_id = models.CharField(max_length=100, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=20, choices=[
#         ('reserved', 'رزرو شده'),
#         ('cancelled', 'لغو شده'),
#         ('done', 'انجام شده')
#     ], default='reserved')
#
# class TimeBlock(models.Model):
#     date = models.DateField()
#     start_time = models.TimeField()
#     end_time = models.TimeField()
#     reason = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)


# class Reservation(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
#     start_datetime = models.DateTimeField()
#     end_datetime = models.DateTimeField()
#     is_paid = models.BooleanField(default=False)
#     deposit_amount = models.PositiveIntegerField()
#     zarinpal_transaction_id = models.CharField(max_length=100, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=20, choices=[
#         ('reserved', 'رزرو شده'),
#         ('cancelled', 'لغو شده'),
#         ('done', 'انجام شده')
#     ], default='reserved')
#
#     def __str__(self):
#         return f"{self.user} - {self.service_type} @ {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"
#
# class TimeBlock(models.Model):
#     date = models.DateField()
#     start_time = models.TimeField()
#     end_time = models.TimeField()
#     reason = models.TextField(blank=True, null=True)  # توضیح دلخواه مدیر
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"Blocked: {self.date} from {self.start_time} to {self.end_time}"
#


# class Categories(models.Model):
#     name = models.CharField(max_length=100)
#     price = models.DecimalField(max_digits=10, decimal_places=3)
#     image = models.ImageField(upload_to='categories_images/',null=True, blank=True)
#     text=models.TextField()
#     slug = models.SlugField()
#     def __str__(self):
#         return self.name
# # Create your models here.
# class Service(models.Model):
#     name = models.CharField(max_length=100)
#     category = models.ForeignKey(Categories, on_delete=models.CASCADE)
#     duration=models.DurationField()
#     price = models.DecimalField(max_digits=10, decimal_places=3)
#     active = models.BooleanField(default=True)
#     image = models.ImageField(upload_to='services_images/',null=True, blank=True)
#     text=models.TextField()
#     slug = models.SlugField()
#
#     def __str__(self):
#         return self.name
# class Reservation(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Customer who books
#     service = models.ForeignKey(Service, on_delete=models.CASCADE)
#     date = models.DateField()  # Booking date
#     time = models.TimeField()  # Booking time
#     created_at = models.DateTimeField(auto_now_add=True)
#
#
#     def __str__(self):
#         return f"{self.user} - {self.service} on {self.date} at {self.time}"



# class Service(models.Model):
#     name = models.CharField(max_length=100)
#     duration_minutes = models.PositiveIntegerField()  # مدت‌زمان هر خدمت به دقیقه
#     deposit_amount = models.PositiveIntegerField()  # بیعانه به تومان
#
#     def __str__(self):
#         return self.name
#
# class Appointment(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     service = models.ForeignKey(Service, on_delete=models.CASCADE)
#     date = models.DateField()
#     start_time = models.TimeField()
#     end_time = models.TimeField()
#     is_paid = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.user} - {self.service} - {self.date} @ {self.start_time}"
#
# class BlockedTime(models.Model):
#     date = models.DateField()
#     start_time = models.TimeField()
#     end_time = models.TimeField()
#     reason = models.CharField(max_length=255, blank=True, null=True)  # برای توضیح مدیر
#
#     def __str__(self):
#         return f"Blocked on {self.date} from {self.start_time} to {self.end_time}"