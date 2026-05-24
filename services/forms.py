# from django import forms
# from .models import Reservation
from django import forms
from .models import AppointmentSlot ,Service
from django.utils.text import slugify
from datetime import time
from .utils.jalali import parse_jalali_to_gregorian ,gregorian_to_jalali_str
import jdatetime
from datetime import time, date


class DateChooseForm(forms.Form):
    date = forms.DateField(input_formats=['%Y-%m-%d'])  # فرانت: جلالی→ISO میلادی

class TimeChooseForm(forms.Form):
    slot_id = forms.IntegerField()


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'title',
            'slug',
            'description',
            'image',
            'deposit_amount_toman',
            'duration_minutes',
            'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'border rounded px-3 py-2 w-full',
                'placeholder': 'مثلاً: خدمات کوتاهی مو'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'border rounded px-3 py-2 w-full',
                'placeholder': 'kootahi-mo',
                'dir': 'ltr'
            }),
            'description': forms.Textarea(attrs={
                'class': 'border rounded px-3 py-2 w-full',
                'rows': 4,
                'placeholder': 'توضیحات سرویس...'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50',
                'accept': 'image/*'
            }),
            'deposit_amount_toman': forms.NumberInput(attrs={
                'class': 'border rounded px-3 py-2 w-full',
                'min': 10000,
                'placeholder': 'مثلاً: 150000'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'border rounded px-3 py-2 w-full',
                'min': 5,
                'placeholder': 'مدت (دقیقه)؛ مثلاً: 60'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded'}),
        }

    def clean_slug(self):
        s = self.cleaned_data.get('slug') or ''
        s = slugify(s.replace('_', '-'))
        if not s:
            s = slugify((self.cleaned_data.get('title') or '').replace('_', '-'))
        return s





def _to_jalali_str(d):
    if not d:
        return ''
    jd = jdatetime.date.fromgregorian(date=d)
    return jd.strftime('%Y/%m/%d')

def _normalize_digits(s: str) -> str:
    # فارسی و عربی → انگلیسی
    tbl = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
    return s.translate(tbl)

class SlotForm(forms.ModelForm):
    # تاریخ را از کاربر به‌صورت جلالی می‌گیریم
    jalali_date = forms.CharField(
        label="تاریخ ",
        widget=forms.TextInput(attrs={
            "class": "border rounded px-3 py-2 w-full",
            "placeholder": "۱۴۰۴/۰۶/۱۲"
        })
    )

    start_time = forms.TimeField(
        label="ساعت شروع",
        input_formats=['%H:%M', '%H:%M:%S'],
        widget=forms.TimeInput(format='%H:%M', attrs={"class": "border rounded px-3 py-2 w-full", "type": "time"})
    )
    end_time = forms.TimeField(
        label="ساعت پایان",
        input_formats=['%H:%M', '%H:%M:%S'],
        widget=forms.TimeInput(format='%H:%M', attrs={"class": "border rounded px-3 py-2 w-full", "type": "time"})
    )

    is_archived = forms.BooleanField(
        label="آرشیو شود",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "rounded border-gray-300"})
    )

    class Meta:
        model = AppointmentSlot
        fields = ['service', 'capacity', 'jalali_date', 'start_time', 'end_time','is_archived']
        widgets = {
            'service': forms.Select(attrs={"class": "border rounded px-3 py-2 w-full"}),
            'capacity': forms.NumberInput(attrs={"class": "border rounded px-3 py-2 w-full", "min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # در حالت ویرایش: اگر date داریم، مقدار اولیهٔ jalali_date را ست کن
        if getattr(self.instance, 'date', None):
            self.fields['jalali_date'].initial = gregorian_to_jalali_str(self.instance.date)



    def clean(self):
        cleaned = super().clean()
        j = cleaned.get('jalali_date')
        if j:
            j = _normalize_digits(j.strip())
            try:
                d = parse_jalali_to_gregorian(j)
                self.instance.date = d
            except Exception as e:
                self.add_error('jalali_date', str(e))
        else:
            # اگر فرم در حالت ایجاد است، تاریخ لازم است
            if not (self.instance and self.instance.pk):
                self.add_error('jalali_date', "تاریخ را وارد کنید.")

        st = cleaned.get('start_time')
        et = cleaned.get('end_time')
        if st and et and et <= st:
            self.add_error('end_time', "ساعت پایان باید بعد از ساعت شروع باشد.")
        return cleaned


WEEKDAY_CHOICES = [
    (5, 'شنبه'),
    (6, 'یکشنبه'),
    (0, 'دوشنبه'),
    (1, 'سه‌شنبه'),
    (2, 'چهارشنبه'),
    (3, 'پنجشنبه'),
    (4, 'جمعه'),
]

class BulkSlotForm(forms.Form):
    MODE_CHOICES = [
        ('dates',   'ساخت بر اساس فهرست تاریخ‌'),
        ('pattern', 'ساخت بر اساس بازهٔ تاریخ + روزهای هفته + گام زمانی'),
    ]
    mode = forms.ChoiceField(
        choices=MODE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'space-y-2'})
    )

    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "border rounded px-3 py-2 w-full"})
    )

    # حالت 1: فهرست تاریخ‌ها (هر خط یک تاریخ جلالی)
    jalali_dates = forms.CharField(
        required=False,
        label="تاریخ‌ها (هر خط یک تاریخ )",
        widget=forms.Textarea(attrs={
            "class": "border rounded px-3 py-2 w-full", "rows": 5,
            "placeholder": "۱۴۰۴/۰۶/۱۲\n۱۴۰۴/۰۶/۱۵"
        })
    )

    # حالت 2: بازه + روزهای هفته + گام
    start_jalali_date = forms.CharField(
        required=False,
        label="تاریخ شروع ",
        widget=forms.TextInput(attrs={"class": "border rounded px-3 py-2 w-full", "placeholder": "۱۴۰۴/۰۶/۰۱"})
    )
    end_jalali_date = forms.CharField(
        required=False,
        label="تاریخ پایان ",
        widget=forms.TextInput(attrs={"class": "border rounded px-3 py-2 w-full", "placeholder": "۱۴۰۴/۰۶/۳۰"})
    )
    weekdays = forms.MultipleChoiceField(
        required=False,
        choices=WEEKDAY_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )
    step_minutes = forms.IntegerField(
        required=False,
        min_value=5, max_value=480,
        label="گام زمانی (دقیقه)",
        widget=forms.NumberInput(attrs={"class": "border rounded px-3 py-2 w-full", "placeholder": "مثلاً 30"})
    )

    # مشترک
    start_time = forms.TimeField(
        label="ساعت شروع", input_formats=['%H:%M'],
        widget=forms.TimeInput(attrs={"class": "border rounded px-3 py-2 w-full", "type": "time"})
    )
    end_time = forms.TimeField(
        label="ساعت پایان", input_formats=['%H:%M'],
        widget=forms.TimeInput(attrs={"class": "border rounded px-3 py-2 w-full", "type": "time"})
    )
    capacity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "border rounded px-3 py-2 w-full"})
    )

    # خروجی validated برای ویو
    cleaned_gdates: list[date] = []
    cleaned_weekdays: set[int] = set()

    def clean(self):
        cleaned = super().clean()
        mode = cleaned.get('mode')
        st = cleaned.get('start_time')
        et = cleaned.get('end_time')

        if st and et and et <= st:
            self.add_error('end_time', "ساعت پایان باید بعد از ساعت شروع باشد.")

        if mode == 'dates':
            # تبدیل لیست تاریخ‌های جلالی به گرگوریان
            lines = [ln.strip() for ln in (cleaned.get('jalali_dates') or '').splitlines() if ln.strip()]
            if not lines:
                self.add_error('jalali_dates', "حداقل یک تاریخ وارد کنید.")
                return cleaned
            gdates = []
            for ln in lines:
                try:
                    gdates.append(parse_jalali_to_gregorian(ln))
                except Exception as e:
                    self.add_error('jalali_dates', f"تاریخ نامعتبر: {ln} — {e}")
                    return cleaned
            self.cleaned_gdates = gdates

        elif mode == 'pattern':
            sj = cleaned.get('start_jalali_date')
            ej = cleaned.get('end_jalali_date')
            wds = cleaned.get('weekdays') or []
            step = cleaned.get('step_minutes')

            if not sj or not ej:
                self.add_error('start_jalali_date', "تاریخ شروع و پایان را وارد کنید.")
                self.add_error('end_jalali_date', "")
                return cleaned
            try:
                sd = parse_jalali_to_gregorian(sj)
                ed = parse_jalali_to_gregorian(ej)
            except Exception as e:
                self.add_error('start_jalali_date', f"خطا در تاریخ: {e}")
                return cleaned

            if sd > ed:
                self.add_error('end_jalali_date', "بازهٔ تاریخ نادرست است (پایان قبل از شروع).")
            if not wds:
                self.add_error('weekdays', "حداقل یک روز هفته را انتخاب کنید.")
            if not step or step <= 0:
                self.add_error('step_minutes', "گام زمانی معتبر نیست.")

            self.cleaned_gdates = [sd, ed]  # در ویو بازه را بسط می‌دهیم
            self.cleaned_weekdays = set(map(int, wds))

        else:
            self.add_error('mode', "حالت ساخت مشخص نیست.")

        return cleaned


# class ReservationForm(forms.ModelForm):
#     class Meta:
#         model = Reservation
#         fields = ['service', 'date', 'time']
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date'}),
#             'time': forms.TimeInput(attrs={'type': 'time'}),
#         }