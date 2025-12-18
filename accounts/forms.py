import re

import jdatetime
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import CustomUser,OtpCode


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('first_name','last_name', 'phone_number')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] and cd['password2'] and cd['password1'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match")
        return cd['password2']

    def save(self,commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text='you cant change password using <a href="../password/">this form</a>.')

    class Meta:
        model = CustomUser

        fields = ('first_name','last_name', 'phone_number', 'password','last_login')

# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = CustomUser
#         fields = ('first_name', 'last_name', 'phone_number', 'birthday', 'password1', 'password2','referraler_code')
#
#     referraler_code='referraler_code'
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         # Set custom labels for fields
#         self.fields['first_name'].label = 'نام'
#         self.fields['last_name'].label = 'نام خانوادگی'
#         self.fields['phone_number'].label = 'شماره موبایل'
#         self.fields['birthday'].label = 'تاریخ تولد'
#         self.fields['password1'].label = 'رمز عبور'
#         self.fields['password2'].label = 'تکرار رمز عبور'
#         self.fields['referraler_code'].label = 'کد معرف (اختیاری)'
#
# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = CustomUser
#         fields = ('phone_number', 'first_name', 'last_name')
#
# class ProfileUpdateForm(forms.ModelForm):
#     class Meta:
#         model = CustomUser
#         fields = ['first_name', 'last_name',]

def fa_to_en_digits(s: str) -> str:
    if not s:
        return s
    map_digits = str.maketrans(
        '۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩',
        '01234567890123456789'
    )
    return s.translate(map_digits)

def normalize_ir_mobile(m: str) -> str:
    """
    نرمال‌سازی شماره موبایل ایران:
    ورودی می‌تواند +98..., 0098..., 98..., 0..., 9... باشد (با فاصله/خط‌تیره/پرانتز/ارقام فارسی)
    خروجی: دقیقاً '98' + 10 رقم (مثلاً 98912xxxxxxx)
    """
    if not m:
        raise ValidationError('شماره موبایل را وارد کنید.')

    m = fa2en_digits(m).strip()
    # حذف کاراکترهای اضافی
    m = re.sub(r'[\s\-\(\)_]', '', m)

    # نرمال‌سازی پیشوندها
    if m.startswith('+98'):
        m = '98' + m[3:]
    elif m.startswith('0098'):
        m = '98' + m[4:]
    elif m.startswith('0') and len(m) == 11 and m.startswith('09'):
        m = '98' + m[1:]             # 0912... -> 98912...
    elif re.fullmatch(r'^9\d{9}$', m):
        m = '98' + m                 # 912... -> 98912...
    elif m.startswith('98'):
        # همان می‌ماند، ولی در انتها طول/الگو چک می‌شود
        pass
    else:
        # سایر حالات پذیرفته نیست
        raise ValidationError('شماره موبایل باید با 09 شروع شود (مثال: 09123456789).')

    # ✅ اعتبارسنجی نهایی: دقیقاً 98 + 10 رقم
    if not re.fullmatch(r'^98\d{10}$', m):
        raise ValidationError('شماره موبایل معتبر نیست. فرمت درست: 09123456789')

    return m

#      register

# ولیداتور با پیام فارسی
ir_phone = RegexValidator(
    regex=r'^(\+?98|0)?9\d{9}$',
    message='شماره موبایل معتبر نیست. فرمت صحیح: ۰۹********* یا +98**********'
)

class UserRegistrationForm(forms.ModelForm):
    phone_number = forms.CharField(
        label='شماره موبایل',
        required=True,
        validators=[ir_phone],
        error_messages={
            'required': 'لطفاً شماره موبایل را وارد کنید.',
            'invalid': 'شماره موبایل معتبر نیست.',  # اگر validator خطا بدهد، این پیام نمایش داده می‌شود
            'min_length': 'شماره موبایل باید دقیقاً ۱۱ رقم و با 09 شروع شود.',
            'max_length': 'شماره موبایل باید دقیقاً ۱۱ رقم و با 09 شروع شود.',
        },
        widget=forms.TextInput(attrs={
            'class': 'form-input ltr',
            'placeholder': 'مثال: 0912xxxxxxx',
            'inputmode': 'tel',
            'dir': 'ltr'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['phone_number']

    def clean_phone_number(self):
        raw = self.cleaned_data.get('phone_number', '')
        raw = fa_to_en_digits(raw)  # تبدیل ارقام فارسی/عربی به انگلیسی

        # اگر خالی بود، پیام required
        if not raw:
            raise ValidationError('لطفاً شماره موبایل را وارد کنید.', code='required')

        # ابتدا روی ورودی خام (بعد از تبدیل ارقام) الگو را چک کن
        try:
            ir_phone(raw)
        except ValidationError:
            # پیام فارسی‌تر و کامل‌تر
            raise ValidationError('شماره موبایل معتبر نیست. فرمت صحیح: ۰۹********* یا +98**********', code='invalid')

        # سپس نرمال‌سازی به 98...
        phone_number = normalize_ir_mobile(raw)

        # بررسی تکراری بودن
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise ValidationError('این شماره قبلاً ثبت شده است.')

        return phone_number



class VerifyCodeForm(forms.Form):
    code = forms.IntegerField()



#      login

def fa2en_digits(s: str) -> str:
    """تبدیل ارقام فارسی/عربی به انگلیسی برای ورودی کاربر"""
    if not s:
        return s
    table = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
    return s.translate(table)


class PhoneLoginForm(forms.Form):
    phone_number = forms.CharField(
        label='شماره موبایل',
        min_length=11,
        max_length=11,  # دقیقاً ۱۱ رقم
        required=True,
        error_messages={
            'required': 'وارد کردن شماره موبایل الزامی است.',
            'min_length': 'شماره موبایل باید دقیقاً ۱۱ رقم و با 09 شروع شود.',
            'max_length': 'شماره موبایل باید دقیقاً ۱۱ رقم و با 09 شروع شود.',
            'invalid': 'شماره موبایل معتبر نیست.',
        },
        widget=forms.TextInput(attrs={
            'class': 'form-input ltr',
            'dir': 'ltr',
            'inputmode': 'numeric',
            'autocomplete': 'tel',
            'placeholder': 'مثال: 0912xxxxxxx',
            'pattern': r'09\d{9}',   # فقط 09 + 9 رقم
            'maxlength': '11',
        })
    )

    def clean_phone_number(self):
        raw = self.cleaned_data.get('phone_number', '') or ''
        raw = fa2en_digits(raw).strip().replace(' ', '').replace('-', '')
        # الزام دقیق: ۱۱ رقم و شروع با 09
        if not re.fullmatch(r'^09\d{9}$', raw):
            raise ValidationError('شماره موبایل باید ۱۱ رقم و با 09 شروع شود.')
        return normalize_ir_mobile(raw)  # خروجی: 98XXXXXXXXX


class OTPVerifyForm(forms.Form):
    code = forms.IntegerField()



#  profile

MIN_YEAR = 1300
MONTHS_FA = [
    (1, "فروردین"), (2, "اردیبهشت"), (3, "خرداد"), (4, "تیر"),
    (5, "مرداد"), (6, "شهریور"), (7, "مهر"), (8, "آبان"),
    (9, "آذر"), (10, "دی"), (11, "بهمن"), (12, "اسفند"),
]

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        label="نام",
        required=True,
        error_messages={'required': 'لطفاً نام را وارد کنید.'},
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'نام'})
    )
    last_name = forms.CharField(
        label="نام خانوادگی",
        required=True,
        error_messages={'required': 'لطفاً نام خانوادگی را وارد کنید.'},
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'نام خانوادگی'})
    )

    # تاریخ تولد (جلالی)
    year = forms.ChoiceField(
        label="سال", required=True,
        error_messages={'required': 'لطفاً سال تولد را انتخاب کنید.'},
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    month = forms.ChoiceField(
        label="ماه", choices=MONTHS_FA, required=True,
        error_messages={'required': 'لطفاً ماه تولد را انتخاب کنید.'},
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    day = forms.ChoiceField(
        label="روز", required=True,
        error_messages={'required': 'لطفاً روز تولد را انتخاب کنید.'},
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'year', 'month', 'day']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            current_jy = jdatetime.date.today().year
        except Exception:
            current_jy = 1404  # fallback اگر سرور timezone/locale مشکل داشت
        self.fields['year'].choices = [(y, y) for y in range(MIN_YEAR, current_jy + 1)]
        self.fields['day'].choices = [(d, d) for d in range(1, 32)]

        # مقداردهی اولیه از پروفایل (اگر تاریخ دارد)
        inst = kwargs.get('instance')
        if inst and getattr(inst, 'birthday', None):
            g = inst.birthday  # date میلادی
            j = jdatetime.date.fromgregorian(day=g.day, month=g.month, year=g.year)
            self.fields['year'].initial = j.year
            self.fields['month'].initial = j.month
            self.fields['day'].initial = j.day

    def clean(self):
        cleaned = super().clean()
        y = cleaned.get('year')
        m = cleaned.get('month')
        d = cleaned.get('day')

        # تبدیل به int + اعتبارسنجی
        try:
            jy = int(y)
            jm = int(m)
            jd = int(d)
        except (TypeError, ValueError):
            if not y:
                self.add_error('year', 'لطفاً سال تولد را انتخاب کنید.')
            if not m:
                self.add_error('month', 'لطفاً ماه تولد را انتخاب کنید.')
            if not d:
                self.add_error('day', 'لطفاً روز تولد را انتخاب کنید.')
            return cleaned

        # تبدیل جلالی → میلادی
        try:
            jdate = jdatetime.date(jy, jm, jd)
            gdate = jdate.togregorian()
        except ValueError:
            self.add_error('day', 'تاریخ وارد شده معتبر نیست.')
            return cleaned

        cleaned['birthday_greg'] = gdate
        return cleaned

    def save(self, commit=True):
        inst = super().save(commit=False)
        gdate = self.cleaned_data.get('birthday_greg')
        if gdate:
            inst.birthday = gdate
        if commit:
            inst.save()
        return inst