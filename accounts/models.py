from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid  # For generating unique recommender codes
from django.utils import timezone
from .managers import CustomUserManager
from django.utils.functional import cached_property
from django.conf import settings
# Create your models here.


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(regex=r'^(\+?98|0)?9\d{9}$')
    phone_number = models.CharField(max_length=15, validators=[phone_regex], unique=True)  # Phone number
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    birthday = models.DateField(null=True)



    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name} "

    @cached_property
    def is_completed(self):
        return all([
            self.full_name and self.full_name.strip(),
            self.phone_number and self.phone_number.strip(),
            self.birthday
        ])

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'  # Use phone number as the unique identifier
    REQUIRED_FIELDS = []  # Additional fields required for creating a user

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"




class OtpCode(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)  # 98xxxxxxxxxx
    code = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # افزوده‌ها:
    expires_at = models.DateTimeField(null=True, blank=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    send_count_today = models.PositiveSmallIntegerField(default=0)
    verify_attempts = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f'{self.phone_number} - {self.code} - {self.created_at}'

    # برگشتی‌های سیاست از settings
    @staticmethod
    def _expire_seconds():
        return int(getattr(settings, "OTP_EXPIRE_SECONDS", 180))

    @staticmethod
    def _resend_seconds():
        return int(getattr(settings, "OTP_RESEND_SECONDS", 60))

    @staticmethod
    def _max_verify_attempts():
        return int(getattr(settings, "OTP_MAX_VERIFY_ATTEMPTS", 5))

    @staticmethod
    def _max_sends_per_day():
        return int(getattr(settings, "OTP_MAX_SENDS_PER_DAY", 5))

    def is_expired(self) -> bool:
        return bool(self.expires_at and timezone.now() > self.expires_at)

    def can_resend(self) -> bool:
        if not self.last_sent_at:
            return True
        return (timezone.now() - self.last_sent_at).total_seconds() >= self._resend_seconds()

    def _same_day(self, dt1, dt2) -> bool:
        if not dt1 or not dt2: return False
        return dt1.date() == dt2.date()

    def can_send_today(self) -> bool:
        # اگر امروز اولین باره، OK؛ اگر نه، چک سقف
        now = timezone.now()
        if not self.last_sent_at or not self._same_day(self.last_sent_at, now):
            return True  # روز تازه → شمارنده از نو
        return self.send_count_today < self._max_sends_per_day()

    def inc_send(self):
        now = timezone.now()
        if not self.last_sent_at or not self._same_day(self.last_sent_at, now):
            self.send_count_today = 1
        else:
            self.send_count_today += 1
        self.last_sent_at = now
        self.expires_at = now + timezone.timedelta(seconds=self._expire_seconds())
        self.verify_attempts = 0  # هر بار ارسال، شمارش تلاش تایید ریست می‌شود
        self.save(update_fields=['send_count_today','last_sent_at','expires_at','verify_attempts','updated_at'])

    def inc_verify(self):
        self.verify_attempts += 1
        self.save(update_fields=['verify_attempts','updated_at'])

    def can_verify(self) -> bool:
        return self.verify_attempts < self._max_verify_attempts()

    # سازگار با متدهای قبلی‌ت (backward-compatible)
    def is_resend_allowed(self):
        return self.can_resend()

    @classmethod
    def get_daily_attempts(cls, phone_number):
        # حالا به send_count_today متکی نباش؛ این متد دیگر استفاده نشود
        obj = cls.objects.filter(phone_number=phone_number).first()
        return obj.send_count_today if obj else 0

    @classmethod
    def clear_old_codes(cls, phone_number):
        # دیگر لازم نیست؛ رکورد یک‌تاست. می‌تونی نادیده بگیری.
        return