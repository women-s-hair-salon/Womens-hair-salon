from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid  # For generating unique recommender codes

# Create your models here.
class UserType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        # ref_codes=CustomUser.objects.all().values_list()
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    phone_number = models.CharField(max_length=15, validators=[phone_regex], unique=True)  # Phone number
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE, default=1)  # Default to 'customer'
    date_joined = models.DateTimeField(auto_now_add=True)
    birthday = models.DateField(null=True)
    referral_code = models.CharField(max_length=10,default=str(uuid.uuid4())[:8].upper())
    referraler_code = models.CharField(max_length=8,blank=True,null=True)
    referral_number = models.IntegerField(default=0)



    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'  # Use phone number as the unique identifier
    REQUIRED_FIELDS = []  # Additional fields required for creating a user

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"

