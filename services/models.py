from django.db import models

from accounts.models import CustomUser
# services/models.py
from .choices import SERVICE_CHOICES, SERVICE_DURATIONS, SERVICE_DEPOSITS
from django.conf import settings


class Service(models.Model):
    name = models.CharField(max_length=200)
    deposit = models.PositiveIntegerField()
    duration_minutes = models.PositiveIntegerField()

    def __str__(self):
        return self.name

# تایم قابل رزرو (ادمین از این بخش تایم‌ها را می‌سازد)
class TimeSlot(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return f"{self.service.name} - {self.date} {self.time}"

# رزرو کاربر
class Reservation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ('slot',)

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