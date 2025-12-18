from django import forms
from .models import ContactMessage ,ServiceCategory, ServiceItem ,Tutorial, Lesson
from django.core.validators import RegexValidator


#   ContactForm

def _normalize_digits(s: str | None) -> str | None:
    if s is None:
        return s
    trans = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
    return s.translate(trans).strip()

_phone_validator = RegexValidator(
    regex=r'^(?:\+?98|0)?9\d{9}$',
    message='شماره موبایل معتبر نیست. مثال: 09123456789 یا +989123456789'
)

class ContactForm(forms.ModelForm):
    full_name = forms.CharField(
        label='نام کامل',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        error_messages={
            'required': 'لطفاً نام کامل را وارد کنید.',
            'max_length': 'نام کامل طولانی است.',
        },
    )

    email = forms.EmailField(
        label='ایمیل',
        required=True,  # اگر اجباری‌اش می‌خواهی True کن
        widget=forms.EmailInput(attrs={'class': 'form-input', 'dir': 'ltr'}),
        error_messages={
            'required': 'لطفاً ایمیل را وارد کنید.',
            'invalid':  'ایمیل معتبر نیست.',
        },
    )

    phone = forms.CharField(
        label='شماره موبایل',
        widget=forms.TextInput(attrs={
            'class': 'form-input', 'placeholder': 'مثلاً 09123456789', 'dir': 'ltr', 'inputmode': 'numeric'
        }),
        error_messages={'required': 'لطفاً شماره موبایل را وارد کنید.'},
        validators=[_phone_validator],
    )

    message = forms.CharField(
        label='پیام',
        widget=forms.Textarea(attrs={'class': 'form-textarea', 'rows': 5}),
        error_messages={'required': 'لطفاً پیام خود را بنویسید.'},
    )

    class Meta:
        model  = ContactMessage
        fields = ['full_name', 'email', 'phone', 'message']

    # نرمال‌سازی/اعتبارسنجی‌های تک‌فیلدی
    def clean_full_name(self):
        return (self.cleaned_data.get('full_name') or '').strip()

    def clean_phone(self):
        phone = _normalize_digits(self.cleaned_data.get('phone') or '')
        if not phone:
            raise forms.ValidationError('لطفاً شماره موبایل را وارد کنید.')
        # تبدیل +98/98 به 0
        if phone.startswith('+98'):
            phone = '0' + phone[3:]
        elif phone.startswith('98'):
            phone = '0' + phone[2:]
        # الگو: 09XXXXXXXXX
        import re
        if not re.fullmatch(r'09\d{9}', phone):
            raise forms.ValidationError('شماره موبایل معتبر نیست. مثال: 09123456789')
        return phone

    def clean_message(self):
        return (self.cleaned_data.get('message') or '').strip()

#       admin

class MessageReplyForm(forms.Form):
    subject = forms.CharField(
        label='موضوع',
        max_length=200,
        widget=forms.TextInput(attrs={'class':'form-input', 'placeholder':'موضوع ایمیل'}),
        error_messages={'required':'موضوع را وارد کنید.'}
    )
    body = forms.CharField(
        label='متن پیام',
        widget=forms.Textarea(attrs={'class':'form-textarea', 'rows':6, 'placeholder':'متن پاسخ شما...'}),
        error_messages={'required':'متن پیام را وارد کنید.'}
    )
    send_copy_to_me = forms.BooleanField(
        label='یک کپی برای من ارسال شود',
        required=False
    )


#   Service

class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ["title", "description", "image"]  # slug خودش در save ساخته می‌شود
        widgets = {
            "title":       forms.TextInput(attrs={"class":"form-input", "placeholder":"مثلاً: گریم عروس"}),
            "description": forms.Textarea(attrs={"class":"form-textarea", "rows":4, "placeholder":"توضیحات دسته…"}),
            "image":       forms.ClearableFileInput(attrs={"class":"form-input"}),
        }

class ServiceItemForm(forms.ModelForm):
    class Meta:
        model = ServiceItem
        fields = ["category", "name", "description", "image"]
        widgets = {
            "category":    forms.Select(attrs={"class":"form-select"}),
            "name":        forms.TextInput(attrs={"class":"form-input", "placeholder":"مثلاً: کاشت ناخن کلاسیک"}),
            "description": forms.Textarea(attrs={"class":"form-textarea", "rows":5, "placeholder":"توضیحات خدمت…"}),
            "image":       forms.ClearableFileInput(attrs={"class":"form-input"}),
        }


#       Tutorial

class TutorialForm(forms.ModelForm):
    class Meta:
        model = Tutorial
        fields = ["title", "description", "cover", "is_published"]
        widgets = {
            "title":       forms.TextInput(attrs={"class":"form-input","placeholder":"عنوان آموزش"}),
            "description": forms.Textarea(attrs={"class":"form-textarea","rows":5,"placeholder":"توضیحات آموزش"}),
            "cover":       forms.ClearableFileInput(attrs={"class":"form-input"}),
            "is_published":forms.CheckboxInput(attrs={"class":"rounded"}),
        }

class LessonForm(forms.ModelForm):
    # پیام خطای URL به فارسی
    video_url  = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={"class":"form-input", "placeholder":"مثلاً: https://youtu.be/…"}),
        error_messages={"invalid": "آدرس ویدیو معتبر نیست."}
    )
    # ورودی فایل با محدودیت client-side
    video_file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "class":"form-input",
            # پسوندهای مجاز (هم‌راستا با Validator مدل)
            "accept": ".mp4,.webm,.ogg,.mov,.m4v,.mkv"
        })
    )
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class":"form-input", "accept":"image/*"})
    )

    class Meta:
        model  = Lesson
        fields = ["tutorial", "title", "description", "image", "video_url", "video_file"]
        widgets = {
            "tutorial":    forms.Select(attrs={"class":"form-select"}),
            "title":       forms.TextInput(attrs={"class":"form-input", "placeholder":"مثلاً: اصول رنگ و مش"}),
            "description": forms.Textarea(attrs={"class":"form-textarea", "rows":4, "placeholder":"توضیحات درس…"}),
        }

    def clean(self):
        cleaned = super().clean()
        url  = cleaned.get("video_url")
        file = cleaned.get("video_file")

        # پیام‌های فارسی برای شرط‌های فرم
        if not url and not file:
            self.add_error("video_url", "یکی از «آدرس ویدیو» یا «فایل ویدیو» الزامی است.")
        if url and file:
            self.add_error("video_file", "فقط یکی را پر کنید، نه هر دو.")
        return cleaned