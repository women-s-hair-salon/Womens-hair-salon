from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.core.validators import RegexValidator

#   AboutUs

class AboutGalleryImage(models.Model):
    image = models.ImageField(upload_to='about/gallery/')
    title = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title or f"About image #{self.pk}"



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
    full_name = models.CharField(max_length=120)
    email     = models.EmailField(blank=True, null=True)   # پاسخ ایمیلی اختیاری
    phone     = models.CharField(max_length=20, blank=True)
    message   = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # فیلدهای پیگیری پاسخ
    is_replied   = models.BooleanField(default=False)
    replied_at   = models.DateTimeField(blank=True, null=True)
    replied_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.SET_NULL, related_name='contact_replies'
    )
    reply_subject = models.CharField(max_length=200, blank=True)
    reply_body    = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'پیام کاربر'
        verbose_name_plural = 'پیام‌های کاربران'

    def __str__(self):
        return f'{self.full_name} - {self.created_at:%Y-%m-%d %H:%M}'

#      Tutorial


class Tutorial(models.Model):
    title = models.CharField(max_length=160, verbose_name="عنوان")
    slug  = models.SlugField(unique=True, blank=True, allow_unicode=True)
    description = models.TextField(blank=True, verbose_name="توضیحات")
    cover = models.ImageField(upload_to="tutorials/cover/", blank=True, null=True, verbose_name="تصویر کاور")
    is_published = models.BooleanField(default=True, verbose_name="انتشار")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "آموزش"
        verbose_name_plural = "آموزش‌ها"

    def __str__(self): return self.title
    def save(self, *a, **kw):
        if not self.slug: self.slug = slugify(self.title, allow_unicode=True)
        return super().save(*a, **kw)


class Lesson(models.Model):
    tutorial    = models.ForeignKey('Tutorial', related_name='lessons', on_delete=models.CASCADE)
    title       = models.CharField(max_length=150, verbose_name="عنوان")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    image       = models.ImageField(upload_to='tutorial_images/', blank=True, null=True, verbose_name="تصویر")
    # یکی از این دو:
    video_url   = models.URLField(blank=True, null=True, verbose_name="آدرس ویدیو")
    video_file = models.FileField(
        upload_to='tutorial_videos/', blank=True, null=True, verbose_name="فایل ویدیو",
        validators=[FileExtensionValidator(
            allowed_extensions=['mp4', 'webm', 'ogg', 'mov', 'm4v', 'mkv'],  # ← MKV اضافه شد
            message='پسوند «%(extension)s» مجاز نیست. پسوندهای مجاز: %(allowed_extensions)s'
        )]
    )

    class Meta:
        verbose_name = "درس"
        verbose_name_plural = "درس‌ها"
        ordering = ['id']

    def clean(self):
        super().clean()
        if not self.video_url and not self.video_file:
            raise ValidationError("یا آدرس ویدیو را بدهید، یا فایل ویدیو را آپلود کنید.")
        if self.video_url and self.video_file:
            raise ValidationError("فقط یکی از «آدرس ویدیو» یا «فایل ویدیو» را پر کنید.")

    def __str__(self):
        return f"{self.tutorial} — {self.title}"