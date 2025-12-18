# services/views_staff.py
from django import forms
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import authenticate
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, FormView, ListView, CreateView, UpdateView, DeleteView ,View
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q ,Count, Prefetch
from accounts.models import CustomUser
from .forms import BulkSlotForm ,SlotForm ,ServiceForm
from .models import AppointmentSlot, Service ,Reservation
from .mixins import StaffRequiredMixin, StaffStepUpRequiredMixin
from django.db import IntegrityError, transaction
from datetime import datetime, timedelta, date, time as dtime
from django.core.exceptions import PermissionDenied
import jdatetime
from django.db.models.deletion import ProtectedError
from .utils.jalali import gregorian_to_jalali_str



class StaffServiceListView(StaffStepUpRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = 'staff/service_list.html'
    context_object_name = 'services'
    permission_required = ('services.view_service',)
    paginate_by = 30

    def get_queryset(self):
        today = timezone.localdate()

        qs = (Service.objects
              .annotate(
                  upcoming_slots=Count('slots', filter=Q(slots__date__gte=today), distinct=True),
                  booked_count=Count('reservations', filter=Q(reservations__status=Reservation.Status.BOOKED),
                                     distinct=True),
              )
              .order_by('-is_active', 'title')
        )

        # فیلتر اختیاری وضعیت
        state = self.request.GET.get('state', 'all')
        if state == 'active':
            qs = qs.filter(is_active=True)
        elif state == 'inactive':
            qs = qs.filter(is_active=False)

        # جستجو اختیاری
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(slug__icontains=q) |
                Q(description__icontains=q)
            )

        return qs


class StaffServiceCreateView(StaffStepUpRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = 'staff/service_form.html'
    form_class = ServiceForm
    success_url = reverse_lazy('staff_services')
    permission_required = ('services.add_service',)

    def form_valid(self, form):
        messages.success(self.request, 'سرویس با موفقیت ایجاد شد.')
        return super().form_valid(form)

class StaffServiceUpdateView(StaffStepUpRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'staff/service_form.html'
    form_class = ServiceForm
    model = Service
    success_url = reverse_lazy('staff_services')
    permission_required = ('services.change_service',)

    def form_valid(self, form):
        messages.success(self.request, 'تغییرات سرویس ذخیره شد.')
        return super().form_valid(form)

class StaffServiceDeleteView(StaffStepUpRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('services.delete_service',)

    def post(self, request, pk):
        svc = get_object_or_404(Service, pk=pk)
        try:
            svc.delete()
            messages.success(request, 'سرویس حذف شد.')
        except ProtectedError:
            messages.error(request, 'این سرویس وابستگی دارد (تایم/رزرو). حذف ممکن نیست؛ آن را غیرفعال (آرشیو) کنید.')
        return redirect('staff_services')

class StaffServiceToggleActiveView(StaffStepUpRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('services.change_service',)

    def post(self, request, pk):
        svc = get_object_or_404(Service, pk=pk)
        svc.is_active = not svc.is_active
        svc.save(update_fields=['is_active'])
        messages.success(request, f'وضعیت سرویس «{svc.title}» به‌روزرسانی شد.')
        return redirect('staff_services')







# -------- Step-Up (فرم رمز) --------
class StaffStepUpForm(forms.Form):
    password = forms.CharField(
        label='رمز مدیریت',
        widget=forms.PasswordInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder':'رمز عبور'})
    )

class StaffStepUpView(StaffRequiredMixin, FormView):
    template_name = 'staff/stepup.html'
    form_class = StaffStepUpForm

    def form_valid(self, form):
        user = self.request.user
        pwd = form.cleaned_data['password']

        # نکته مهم: authenticate با username=USER.USERNAME_FIELD
        u = authenticate(self.request, username=user.phone_number, password=pwd)
        if u is None or u.pk != user.pk:
            form.add_error('password', 'رمز نادرست است یا برای حساب شما تنظیم نشده است.')
            return self.form_invalid(form)

        if not user.has_usable_password():
            form.add_error('password', 'برای این حساب هنوز رمز تنظیم نشده. با مدیر سیستم تماس بگیرید.')
            return self.form_invalid(form)

        # موفق: فلگ سشن بگذار
        self.request.session['staff_stepup_verified_at'] = timezone.now().timestamp()
        next_url = self.request.session.pop('staff_next', None) or reverse('staff_dashboard')
        return redirect(next_url)

# قفل مجدد (اختیاری: خروج از حالت step-up)
class StaffLockView(StaffRequiredMixin, TemplateView):
    template_name = 'staff/locked.html'
    def get(self, request, *args, **kwargs):
        request.session.pop('staff_stepup_verified_at', None)
        return redirect('staff_stepup')

# -------- داشبورد --------
class StaffDashboardView(StaffStepUpRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'staff/dashboard.html'
    permission_required = ('services.view_appointmentslot',)

    def get_context_data(self, **kwargs):
        from .models import Reservation
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        ctx['users_count'] = CustomUser.objects.count()
        ctx['upcoming_slots'] = (AppointmentSlot.objects
                                 .filter(date__gte=today, is_archived=False)
                                 .order_by('date','start_time')[:10])
        ctx['services'] = Service.objects.filter(is_active=True)
        ctx['pending_res_count'] = Reservation.objects.filter(status=Reservation.Status.PENDING).count()
        ctx['booked_res_count']  = Reservation.objects.filter(status=Reservation.Status.BOOKED).count()
        return ctx

# -------- کاربران --------
def _normalize_digits(s: str) -> str:
    if not s: return s
    trans = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
    return s.translate(trans)

class StaffUserListView(StaffStepUpRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = 'staff/users.html'
    model = CustomUser
    context_object_name = 'users'
    paginate_by = 25
    permission_required = ('accounts.view_customuser',)

    def get_queryset(self):
        qs = CustomUser.objects.all().order_by('-created_at')
        q = self.request.GET.get('q', '') or ''
        q = _normalize_digits(q).strip()
        if q:
            tokens = [t for t in q.split() if t]
            for t in tokens:
                qs = qs.filter(
                    Q(phone_number__icontains=t) |
                    Q(first_name__icontains=t) |
                    Q(last_name__icontains=t)
                )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_users'] = CustomUser.objects.count()

        # تعداد «افراد»ی که رزرو BOOKED دارند (distinct روی user_id)
        ctx['total_booked_users'] = (
            Reservation.objects
            .filter(status=Reservation.Status.BOOKED)
            .values('user_id').distinct()
            .count()
        )

        # تعداد کل رزروهای BOOKED
        ctx['total_booked_reservations'] = (
            Reservation.objects.filter(status=Reservation.Status.BOOKED).count()
        )
        return ctx

# -------- مدیریت اسلات‌ها (CRUD) --------
class SlotListView(StaffStepUpRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = 'staff/slot_list.html'
    model = AppointmentSlot
    context_object_name = 'slots'
    permission_required = ('services.view_appointmentslot',)
    paginate_by = 25  # اگر خواستی صفحه‌بندی

    def get_queryset(self):
        qs = AppointmentSlot.objects.order_by('-date', 'start_time')
        svc = self.request.GET.get('service')
        if svc:
            qs = qs.filter(service_id=svc)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from .models import Service
        ctx['services'] = Service.objects.filter(is_active=True)
        return ctx

class SlotCreateView(StaffStepUpRequiredMixin, PermissionRequiredMixin, CreateView):
    model = AppointmentSlot
    form_class = SlotForm
    template_name = 'staff/slot_form.html'
    success_url = reverse_lazy('staff_slots')
    permission_required = ('services.add_appointmentslot',)

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = form.save()  # date قبلاً در clean روی instance ست شد
        except IntegrityError as e:
            form.add_error(None, "ذخیره امکان‌پذیر نبود (تکراری یا مغایرت داده).")
            return self.form_invalid(form)
        messages.success(self.request, "تایم با موفقیت ایجاد شد.")
        return redirect(self.success_url)

    def form_invalid(self, form):
        # خطاها در قالب نمایش داده می‌شوند
        messages.error(self.request, "فرم نامعتبر است. موارد قرمز را بررسی کنید.")
        return super().form_invalid(form)

class SlotUpdateView(StaffStepUpRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = AppointmentSlot
    form_class = SlotForm
    template_name = 'staff/slot_form.html'
    success_url = reverse_lazy('staff_slots')
    permission_required = ('services.change_appointmentslot',)

    def get_initial(self):
        ini = super().get_initial()
        obj = self.get_object()
        ini['jalali_date'] = gregorian_to_jalali_str(obj.date)  # خروجی مثل 1404/06/12
        return ini

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = form.save()
        except IntegrityError:
            form.add_error(None, "ذخیره امکان‌پذیر نبود (تکراری یا مغایرت داده).")
            return self.form_invalid(form)
        messages.success(self.request, "تایم با موفقیت ویرایش شد.")
        return redirect(self.success_url)

class SlotDeleteView(StaffStepUpRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = AppointmentSlot
    template_name = 'staff/slot_confirm_delete.html'
    success_url = reverse_lazy('staff_slots')
    permission_required = ('services.delete_appointmentslot',)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # 1) جلوگیری از حذف وقتی رزرو فعال دارد
        has_active = self.object.reservations.filter(
            status__in=[Reservation.Status.PENDING, Reservation.Status.BOOKED]
        ).exists()
        if has_active:
            messages.error(request, 'این تایم رزرو فعال دارد و قابل حذف نیست. لطفاً آن را آرشیو کنید.')
            return redirect(self.success_url)

        # 2) حذف ایمن: رزروهای غیرفعال پاک شود، سپس اسلات
        with transaction.atomic():
            self.object.reservations.filter(
                status__in=[Reservation.Status.FAILED, Reservation.Status.EXPIRED, Reservation.Status.CANCELED]
            ).delete()
            self.object.delete()

        messages.success(request, 'تایم با موفقیت حذف شد.')
        return redirect(self.success_url)

    # اختیاری: برای نمایش هشدار در قالب تأیید حذف
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        slot = self.object
        ctx['has_active'] = slot.reservations.filter(
            status__in=[Reservation.Status.PENDING, Reservation.Status.BOOKED]
        ).exists()
        return ctx

# بازهٔ تاریخی بدهد، روزهای هفته (شنبه تا جمعه)

class BulkSlotCreateView(StaffStepUpRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = 'staff/slot_bulk_form.html'
    form_class = BulkSlotForm
    permission_required = ('services.add_appointmentslot',)
    success_url = reverse_lazy('staff_slots')

    def form_valid(self, form: BulkSlotForm):
        svc = form.cleaned_data['service']
        st  = form.cleaned_data['start_time']
        et  = form.cleaned_data['end_time']
        cap = form.cleaned_data['capacity']
        mode= form.cleaned_data['mode']

        created = 0
        skipped = 0

        @transaction.atomic
        def create_for_date(d: date):
            nonlocal created, skipped
            # در حالت dates: یک اسلات (تکی)  → اگر می‌خواهی یک اسلات بلند بسازی
            if mode == 'dates' and st and et:
                exists = AppointmentSlot.objects.filter(
                    service=svc, date=d, start_time=st, end_time=et
                ).exists()
                if exists:
                    skipped += 1
                    return
                AppointmentSlot.objects.create(
                    service=svc, date=d, start_time=st, end_time=et, capacity=cap
                )
                created += 1
                return

            # در حالت pattern: بازه را به اسلات‌های step می‌شکنیم
            step = form.cleaned_data.get('step_minutes') or 0
            current = datetime.combine(d, st)
            end_dt  = datetime.combine(d, et)
            while current < end_dt:
                next_dt = current + timedelta(minutes=step)
                if next_dt <= end_dt:
                    exists = AppointmentSlot.objects.filter(
                        service=svc, date=d,
                        start_time=current.time(), end_time=next_dt.time()
                    ).exists()
                    if exists:
                        skipped += 1
                    else:
                        AppointmentSlot.objects.create(
                            service=svc, date=d,
                            start_time=current.time(), end_time=next_dt.time(),
                            capacity=cap
                        )
                        created += 1
                current = next_dt

        # شاخه‌ی اجرای دو حالت
        if form.cleaned_data['mode'] == 'dates':
            for d in form.cleaned_gdates:
                create_for_date(d)
        else:
            sd, ed = form.cleaned_gdates  # بازهٔ گرگوریان
            wds = form.cleaned_weekdays   # set[int]
            d = sd
            while d <= ed:
                if d.weekday() in wds:
                    create_for_date(d)
                d += timedelta(days=1)

        if created:
            messages.success(self.request, f"{created} تایم ایجاد شد. (رد شده: {skipped})")
        else:
            messages.warning(self.request, "تایمی ایجاد نشد. (شاید همه تکراری بودند)")

        return super().form_valid(form)


class StaffReservationListView(StaffStepUpRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = 'staff/reservations.html'
    context_object_name = 'items'
    paginate_by = 25
    permission_required = ('services.view_reservation',)

    def get_queryset(self):
        qs = (Reservation.objects
              .select_related('user','service','slot')
              .filter(status=Reservation.Status.BOOKED)
              .order_by('-created_at'))
        q = (self.request.GET.get('q') or '').strip()
        if q:
            # نرمال‌سازی ارقام فارسی/عربی
            trans = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
            qn = q.translate(trans)
            qs = qs.filter(
                Q(user__phone_number__icontains=qn) |
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(service__title__icontains=q)
            )
        # فیلتر تاریخ (اختیاری): ?date=YYYY-MM-DD
        d = (self.request.GET.get('date') or '').strip()
        if d:
            qs = qs.filter(slot__date=d)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_users'] = CustomUser.objects.count()

        # تعداد «افراد»ی که رزرو BOOKED دارند (distinct روی user_id)
        ctx['total_booked_users'] = (
            Reservation.objects
            .filter(status=Reservation.Status.BOOKED)
            .values('user_id').distinct()
            .count()
        )

        # تعداد کل رزروهای BOOKED
        ctx['total_booked_reservations'] = (
            Reservation.objects.filter(status=Reservation.Status.BOOKED).count()
        )
        return ctx