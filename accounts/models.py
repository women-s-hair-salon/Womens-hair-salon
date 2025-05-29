from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid  # For generating unique recommender codes
from django.utils import timezone
from .managers import CustomUserManager


# Create your models here.


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
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
        return f"{self.first_name} {self.last_name}"

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'  # Use phone number as the unique identifier
    REQUIRED_FIELDS = []  # Additional fields required for creating a user

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"




class OtpCode(models.Model):
    phone_number = models.CharField(max_length=11, unique=True)
    code = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.phone_number} - {self.code} - {self.created_at}'

    def is_resend_allowed(self):
        # بررسی اینکه آیا از زمان ایجاد بیش از ۶۰ ثانیه گذشته؟
        return (timezone.now() - self.created_at).total_seconds() > 60

    @classmethod
    def get_daily_attempts(cls, phone_number):
        """تعداد تلاش‌های ارسال کد OTP در ۲۴ ساعت گذشته"""
        now = timezone.now()
        start_of_day = now - timezone.timedelta(days=1)
        return cls.objects.filter(phone_number=phone_number, created_at__gte=start_of_day).count()

    @classmethod
    def clear_old_codes(cls, phone_number):
        """حذف کدهای قدیمی‌تر از ۲۴ ساعت"""
        now = timezone.now()
        start_of_day = now - timezone.timedelta(days=1)
        cls.objects.filter(phone_number=phone_number, created_at__lt=start_of_day).delete()