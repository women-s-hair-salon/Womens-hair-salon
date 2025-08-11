from django.db import models
from django.utils.text import slugify
from django.core.validators import RegexValidator

#  services
class ServiceCategory(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="توضیحات")
    image = models.ImageField(upload_to="category_images/", verbose_name="تصویر",default='default.jpg')

    class Meta:
        verbose_name = "دسته‌بندی خدمات"
        verbose_name_plural = "دسته‌بندی‌های خدمات"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


class ServiceItem(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=100, verbose_name="نام خدمت")
    description = models.TextField(verbose_name="توضیحات خدمت")
    image = models.ImageField(upload_to="service_images/", verbose_name="تصویر خدمت")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "جزئیات خدمات"
        verbose_name_plural = "جزئیات های خدمات"


#  Contact Us


iranian_mobile_validator = RegexValidator(
    regex=r'^09\d{9}$',
    message="شماره موبایل باید با 09 شروع شده و 11 رقم باشد."
)


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="نام کامل")
    email = models.EmailField(verbose_name="ایمیل")
    phone = models.CharField(max_length=11, validators=[iranian_mobile_validator], verbose_name="شماره موبایل")
    message = models.TextField(verbose_name="پیام")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")

    class Meta:
        verbose_name = "پیام تماس با ما"
        verbose_name_plural = "پیام‌های تماس با ما"

    def __str__(self):
        return f"{self.full_name} - {self.created_at.strftime('%Y-%m-%d')}"