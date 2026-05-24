from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from accounts.forms import UserRegistrationForm, VerifyCodeForm, PhoneLoginForm, OTPVerifyForm, ProfileUpdateForm, \
    normalize_ir_mobile
from accounts.models import CustomUser ,OtpCode
import random
from utils import send_otp_code
from django.contrib.auth import logout
from django.db import transaction
import logging
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
import jdatetime
from datetime import datetime
from django.http import JsonResponse
from django.utils.translation import gettext as _
# register
OTP_LENGTH = 6  # ← طول OTP را اینجا یک‌جا کنترل کن
logger = logging.getLogger(__name__)

class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logger.info(f"User {request.user} tried to access signup page while authenticated.")
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        logger.debug("Signup form requested.")
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            # 1) نرمال‌سازی شماره
            phone_number = normalize_ir_mobile(form.cleaned_data['phone_number'])
            # ۶ رقمی به‌صورت رشته
            random_code = f"{random.randint(10 ** (OTP_LENGTH - 1), 10 ** OTP_LENGTH - 1)}"

            try:
                # 2) ارسال
                ok = send_otp_code(phone_number, random_code)
                if not ok:
                    messages.error(request, 'مشکلی در ارسال کد پیش آمد.')
                    return render(request, self.template_name, {'form': form})

                # 3) ⬅⬅ ذخیرهٔ درست OTP (کلید مشکل شما)
                OtpCode.objects.update_or_create(
                    phone_number=phone_number,
                    defaults={'code': random_code}
                )

                # 4) سشن با شمارهٔ نرمال
                request.session['user_registration_info'] = {
                    'phone_number': phone_number,
                    'otp_sent_at': timezone.now().timestamp(),
                }

                messages.success(request, 'کد برای شما ارسال شد.', 'success')
                return redirect('verify_code')

            except Exception as e:
                logger.error(f"Failed to send OTP to {phone_number}: {str(e)}")
                messages.error(request, 'مشکلی در ارسال کد پیش آمد.')
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, error)

        return render(request, self.template_name, {'form': form})


class UserRegisterVerifyCodeView(View):
    form_class = VerifyCodeForm

    def get(self, request):
        user_session = request.session.get('user_registration_info')
        if not user_session:
            logger.warning("No session found for registration verification.")
            messages.error(request, 'اطلاعاتی برای تأیید یافت نشد.', 'danger')
            return redirect('signup')

        logger.debug(f"Rendering OTP verification page for {user_session['phone_number']}")
        return render(request, 'verify.html', {
            'form': self.form_class(),
            'otp_sent_at': user_session.get('otp_sent_at'),
            'phone': user_session.get('phone_number'),
        })

    def post(self, request):
        user_session = request.session.get('user_registration_info')
        if not user_session:
            messages.error(request, 'اطلاعاتی برای تأیید یافت نشد.', 'danger')
            return redirect('signup')

        phone = normalize_ir_mobile(user_session['phone_number'])
        form = self.form_class(request.POST)

        try:
            code_instance = OtpCode.objects.get(phone_number=phone)
        except OtpCode.DoesNotExist:
            messages.error(request, 'کدی برای این شماره پیدا نشد.', 'danger')
            return redirect('verify_code')

        if form.is_valid():
            entered_code = int(form.cleaned_data['code'])
            if entered_code == int(code_instance.code):
                user, created = CustomUser.objects.get_or_create(phone_number=phone)
                login(request, user)
                code_instance.delete()
                messages.success(request, 'ثبت‌نام با موفقیت انجام شد.', 'success')
                return redirect('home')
            else:
                messages.error(request, 'کد وارد شده صحیح نیست.', 'danger')
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, error)

        return render(request, 'verify.html', {
            'form': form,
            'otp_sent_at': user_session.get('otp_sent_at'),
            'phone': phone,
        })


# login

logger = logging.getLogger(__name__)

class UserLoginView(View):
    def get(self, request):
        logger.debug("Login page requested.")
        form = PhoneLoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            phone = normalize_ir_mobile(form.cleaned_data['phone_number'])
            if CustomUser.objects.filter(phone_number=phone).exists():
                try:
                    code = f"{random.randint(10 ** (OTP_LENGTH - 1), 10 ** OTP_LENGTH - 1)}"
                    ok = send_otp_code(phone, code)
                    if not ok:
                        messages.error(request, 'مشکلی در ارسال کد پیش آمد.')
                        return render(request, 'login.html', {'form': form})

                    # ⬅⬅ ذخیرهٔ درست OTP
                    OtpCode.objects.update_or_create(
                        phone_number=phone,
                        defaults={'code': code}
                    )

                    request.session['login_phone'] = phone
                    request.session['otp_sent_at'] = timezone.now().timestamp()
                    messages.success(request, 'کد برای شما ارسال شد.')
                    return redirect('verify_login_code')
                except Exception as e:
                    logger.error(f"Error sending OTP to {phone}: {str(e)}")
                    messages.error(request, 'مشکلی در ارسال کد پیش آمد.')
            else:
                messages.error(request, 'این شماره ثبت نشده.')
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, error)

        return render(request, 'login.html', {'form': form})


class UserLoginVerifyView(View):
    def get(self, request):
        phone = request.session.get('login_phone')
        otp_sent_at = request.session.get('otp_sent_at')
        logger.debug(f"Rendering login OTP verification page for {phone}")
        form = OTPVerifyForm()
        return render(request, 'verify_login.html', {
            'form': form,
            'otp_sent_at': otp_sent_at,
            'phone': phone
        })

    def post(self, request):
        phone = request.session.get('login_phone')
        if not phone:
            return redirect('login')
        phone = normalize_ir_mobile(phone)

        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            try:
                otp = OtpCode.objects.get(phone_number=phone)
            except OtpCode.DoesNotExist:
                messages.error(request, 'کدی برای این شماره پیدا نشد.')
                return redirect('verify_login_code')

            if int(otp.code) == int(form.cleaned_data['code']):
                user = CustomUser.objects.get(phone_number=phone)
                login(request, user)
                otp.delete()
                messages.success(request, 'با موفقیت وارد شدید.')
                return redirect('home')
            else:
                messages.error(request, 'کد وارد شده صحیح نیست.')
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, error)

        return render(request, 'verify_login.html', {
            'form': form,
            'otp_sent_at': request.session.get('otp_sent_at'),
            'phone': phone
        })


# resend otp

logger = logging.getLogger(__name__)

MAX_ATTEMPTS_PER_DAY = 5  # حداکثر تعداد درخواست‌ها در ۲۴ ساعت

class ResendOtpCodeView(View):
    def get(self, request):
        session_data = request.session.get('user_registration_info')
        login_phone = request.session.get('login_phone')

        if session_data:
            phone = normalize_ir_mobile(session_data.get('phone_number'))
            redirect_to = 'verify_code'
        elif login_phone:
            phone = normalize_ir_mobile(login_phone)
            redirect_to = 'verify_login_code'
        else:
            messages.error(request, 'شماره‌ای برای ارسال کد یافت نشد.', 'danger')
            return redirect('login')

        # سیاست خودت را نگه می‌داریم (تاخیر 60 ثانیه/حداکثر روزانه) – اگر می‌خوای همین فعلی بماند، دخالت نمی‌کنم
        code_instance = OtpCode.objects.filter(phone_number=phone).first()
        if code_instance and not code_instance.is_resend_allowed():
            messages.warning(request, 'لطفاً ۶۰ ثانیه صبر کنید و دوباره امتحان کنید.', 'warning')
            return redirect(redirect_to)

        OtpCode.clear_old_codes(phone)
        daily_attempts = OtpCode.get_daily_attempts(phone)
        if daily_attempts >= MAX_ATTEMPTS_PER_DAY:
            messages.error(request, '۵ بار در ۲۴ ساعت گذشته درخواست دادید. لطفاً فردا امتحان کنید.', 'danger')
            return redirect(redirect_to)

        if code_instance:
            code_instance.delete()

        try:
            random_code = f"{random.randint(10 ** (OTP_LENGTH - 1), 10 ** OTP_LENGTH - 1)}"
            ok = send_otp_code(phone, random_code)
            if not ok:
                messages.error(request, 'ارسال کد با خطا مواجه شد.', 'danger')
                return redirect(redirect_to)

            # ⬅⬅ ذخیرهٔ درست OTP
            OtpCode.objects.update_or_create(
                phone_number=phone,
                defaults={'code': random_code}
            )

            if session_data:
                request.session['user_registration_info']['otp_sent_at'] = timezone.now().timestamp()
            elif login_phone:
                request.session['otp_sent_at'] = timezone.now().timestamp()

            messages.success(request, 'کد جدید ارسال شد.', 'success')
        except Exception as e:
            logger.error(f"Error sending OTP to {phone}: {str(e)}")
            messages.error(request, 'ارسال کد با خطا مواجه شد.', 'danger')

        return redirect(redirect_to)


#  Logout

class UserLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'شما با موفقیت خارج شدید.', 'success')
        return redirect('home')



# profile

class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'profile.html'
    form_class = ProfileUpdateForm

    def _months(self):
        return list(enumerate([
            "فروردین","اردیبهشت","خرداد","تیر","مرداد","شهریور",
            "مهر","آبان","آذر","دی","بهمن","اسفند"
        ], start=1))

    def _initial_birth_parts(self, user):
        """ مقداردهی برای نمایش اولیه در قالب (اختیاری اگر از form.initial استفاده نکنی) """
        if user and getattr(user, 'birthday', None):
            g = user.birthday
            j = jdatetime.date.fromgregorian(day=g.day, month=g.month, year=g.year)
            return j.year, j.month, j.day
        return None, None, None

    def get(self, request):
        form = self.form_class(instance=request.user)
        by, bm, bd = self._initial_birth_parts(request.user)
        ctx = {
            'form': form,
            'months': self._months(),
            'birth_year': by, 'birth_month': bm, 'birth_day': bd,
        }
        return render(request, self.template_name, ctx)

    def post(self, request):
        form = self.form_class(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "تغییرات پروفایل با موفقیت ذخیره شد.")
            return redirect('profile')
        # اگر خطا داشت، همان مقادیر انتخاب‌شده را دوباره به قالب بدهیم
        by = request.POST.get('year')
        bm = request.POST.get('month')
        bd = request.POST.get('day')
        ctx = {
            'form': form,
            'months': self._months(),
            'birth_year': int(by) if by and by.isdigit() else None,
            'birth_month': int(bm) if bm and str(bm).isdigit() else None,
            'birth_day': int(bd) if bd and str(bd).isdigit() else None,
        }
        return render(request, self.template_name, ctx)



#
# @login_required
# def reservation_view(request):
#     print(f"full_name: [{request.user.full_name}]")
#     print(f"phone_number: [{request.user.phone_number}]")
#     print(f"birthday: [{request.user.birthday}]")
#     print(f"is_completed: [{request.user.is_completed}]")
#
#     context = {
#         'user_completed': request.user.is_completed
#     }
#     return render(request, 'step_one.html', context)

# @login_required
# def reservation_view(request):
#     form = ProfileUpdateForm(instance=request.user)
#
#     if not form.is_valid():
#         user_completed = False
#     else:
#         user_completed = True
#
#     return render(request, 'reservation.html', {
#         'user_completed': user_completed
#     })
