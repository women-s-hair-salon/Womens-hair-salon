from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from accounts.forms import UserRegistrationForm, VerifyCodeForm ,PhoneLoginForm ,OTPVerifyForm,ProfileUpdateForm
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

# register

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
            phone_number = form.cleaned_data['phone_number']
            random_code = random.randint(1000, 9999)

            try:
                send_otp_code(phone_number, random_code)
                with transaction.atomic():
                    OtpCode.objects.create(phone_number=phone_number, code=random_code)

                request.session['user_registration_info'] = {
                    'phone_number': phone_number,
                    'otp_sent_at': timezone.now().timestamp(),
                }

                logger.info(f"OTP code sent to {phone_number} for registration.")
                messages.success(request, 'We sent you a code', 'success')
                return redirect('verify_code')

            except Exception as e:
                logger.error(f"Failed to send OTP to {phone_number}: {str(e)}")
                messages.error(request, 'مشکلی در ارسال کد پیش آمد.')
        else:
            logger.warning("Signup form is invalid.")
            for field in form.errors:
                for error in form.errors[field]:
                    logger.debug(f"Validation error on field '{field}': {error}")
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
            logger.warning("POST verify code called without session.")
            messages.error(request, 'اطلاعاتی برای تأیید یافت نشد.', 'danger')
            return redirect('signup')

        phone = user_session['phone_number']
        form = self.form_class(request.POST)

        try:
            code_instance = OtpCode.objects.get(phone_number=phone)
        except OtpCode.DoesNotExist:
            logger.error(f"OTP not found for phone: {phone}")
            messages.error(request, 'کدی برای این شماره پیدا نشد.', 'danger')
            return redirect('verify_code')

        if form.is_valid():
            entered_code = form.cleaned_data['code']
            if entered_code == code_instance.code:
                user, created = CustomUser.objects.get_or_create(phone_number=phone)
                login(request, user)
                code_instance.delete()
                logger.info(f"User {phone} verified and {'created' if created else 'logged in'}.")
                messages.success(request, 'ثبت‌نام با موفقیت انجام شد.', 'success')
                return redirect('home')
            else:
                logger.warning(f"Wrong OTP entered for {phone}: {entered_code}")
                messages.error(request, 'کد وارد شده صحیح نیست.', 'danger')
        else:
            logger.warning(f"Invalid form submitted during OTP verification for {phone}")
            for field in form.errors:
                for error in form.errors[field]:
                    logger.debug(f"Validation error on '{field}': {error}")
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
            phone = form.cleaned_data['phone_number']
            if CustomUser.objects.filter(phone_number=phone).exists():
                try:
                    code = random.randint(1000, 9999)
                    send_otp_code(phone, code)
                    OtpCode.objects.update_or_create(phone_number=phone, defaults={'code': code})
                    request.session['login_phone'] = phone
                    request.session['otp_sent_at'] = timezone.now().timestamp()
                    logger.info(f"OTP sent to existing user {phone} for login.")
                    messages.success(request, 'کد برای شما ارسال شد.')
                    return redirect('verify_login_code')
                except Exception as e:
                    logger.error(f"Error sending OTP to {phone}: {str(e)}")
                    messages.error(request, 'مشکلی در ارسال کد پیش آمد.')
            else:
                logger.warning(f"Login attempt with unregistered phone: {phone}")
                messages.error(request, 'این شماره ثبت نشده.')
        else:
            logger.warning("Invalid login form submitted.")
            for field in form.errors:
                for error in form.errors[field]:
                    logger.debug(f"Validation error on '{field}': {error}")
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
            logger.warning("Login verification attempted without phone in session.")
            return redirect('login')

        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            try:
                otp = OtpCode.objects.get(phone_number=phone)
            except OtpCode.DoesNotExist:
                logger.error(f"OTP code not found for phone: {phone}")
                messages.error(request, 'کدی برای این شماره پیدا نشد.')
                return redirect('verify_login_code')

            if otp.code == form.cleaned_data['code']:
                user = CustomUser.objects.get(phone_number=phone)
                login(request, user)
                otp.delete()
                logger.info(f"User {phone} successfully logged in.")
                messages.success(request, 'با موفقیت وارد شدید.')
                return redirect('home')
            else:
                logger.warning(f"Wrong OTP entered for phone: {phone}")
                messages.error(request, 'کد وارد شده صحیح نیست.')
        else:
            logger.warning(f"Invalid OTP form submitted for {phone}")
            for field in form.errors:
                for error in form.errors[field]:
                    logger.debug(f"Validation error on '{field}': {error}")
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
            phone = session_data.get('phone_number')
            redirect_to = 'verify_code'
        elif login_phone:
            phone = login_phone
            redirect_to = 'verify_login_code'
        else:
            logger.warning("Resend OTP attempted without phone in session.")
            messages.error(request, 'شماره‌ای برای ارسال کد یافت نشد.', 'danger')
            return redirect('login')

        logger.debug(f"Attempting to resend OTP for {phone}")

        # حذف کدهای قدیمی‌تر از ۲۴ ساعت
        OtpCode.clear_old_codes(phone)

        # بررسی تعداد تلاش‌های موجود
        daily_attempts = OtpCode.get_daily_attempts(phone)
        remaining_attempts = MAX_ATTEMPTS_PER_DAY - daily_attempts

        if remaining_attempts <= 0:
            logger.warning(f"{phone} exceeded max resend attempts in 24 hours.")
            messages.error(
                request,
                'شما ۵ بار در ۲۴ ساعت گذشته درخواست ارسال کد داشته‌اید. لطفاً فردا دوباره امتحان کنید.',
                'danger'
            )
            return redirect(redirect_to)

        code_instance = OtpCode.objects.filter(phone_number=phone).first()
        if code_instance and not code_instance.is_resend_allowed():
            logger.info(f"{phone} tried to resend OTP before 60 seconds.")
            messages.warning(request, 'لطفاً ۶۰ ثانیه صبر کنید و دوباره امتحان کنید.', 'warning')
            return redirect(redirect_to)

        if code_instance:
            logger.debug(f"Old OTP deleted for {phone}")
            code_instance.delete()

        try:
            random_code = random.randint(1000, 9999)
            send_otp_code(phone, random_code)
            OtpCode.objects.create(phone_number=phone, code=random_code)

            if session_data:
                request.session['user_registration_info']['otp_sent_at'] = timezone.now().timestamp()
            elif login_phone:
                request.session['otp_sent_at'] = timezone.now().timestamp()

            logger.info(f"New OTP sent to {phone}. Remaining attempts: {remaining_attempts - 1}")
            messages.success(
                request,
                f'کد جدید ارسال شد. شما {remaining_attempts - 1} تلاش دیگر دارید.',
                'success'
            )
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
    form_class = ProfileUpdateForm
    template_name = 'profile.html'

    def get(self, request):
        form = self.form_class(instance=request.user)

        # لیست ماه‌های فارسی
        months = list(enumerate([
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ], start=1))

        user = request.user
        context = {
            'form': form,
            'months': months,
            'birth_year': user.birthday.year if user.birthday else None,
            'birth_month': user.birthday.month if user.birthday else None,
            'birth_day': user.birthday.day if user.birthday else None,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST, instance=request.user)

        if form.is_valid():
            try:
                year = int(request.POST.get('year'))
                month = int(request.POST.get('month'))
                day = int(request.POST.get('day'))
                g_date = jdatetime.date(year, month, day).togregorian()

                user = form.save(commit=False)
                user.birthday = g_date
                user.save()

                return JsonResponse({
                    'success': True,
                    'message': 'اطلاعات پروفایل با موفقیت ذخیره شد.'
                })
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': 'تاریخ وارد شده معتبر نیست.'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'لطفاً اطلاعات را به‌درستی وارد کنید.'
            })


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
