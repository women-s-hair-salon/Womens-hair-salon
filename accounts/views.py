from django.core.exceptions import ValidationError
from django.shortcuts import render,redirect
from django.views.generic.list import ListView
from django.contrib.auth import authenticate, login
from .forms import CustomUserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView,UpdateView
from .models import CustomUser
from services.models import Reservation

def signup(request):
    if request.method == 'POST':
        a = CustomUser.objects.all().values_list('referral_code',flat=True)
        form = CustomUserCreationForm(request.POST)
        print(a)
        if form.is_valid():
            referraler_code = form.cleaned_data.get('referraler_code')
            if referraler_code:
                if referraler_code not in a:
                    form.add_error('referraler_code', "Invalid referral code!")
                else:
                    b= CustomUser.objects.filter(referral_code=referraler_code).first()
                    b.referral_number += 1
                    b.save()

                    form.save()
                    return redirect('login')
        else:
            if form.is_valid():
                form.save()
                return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')  # دریافت شماره موبایل
        password = request.POST.get('password')  # دریافت رمز عبور
        user = authenticate(request, username=phone_number, password=password)  # احراز هویت کاربر
        if user is not None:
            login(request, user)  # ورود کاربر
            return redirect('home')  # هدایت به صفحه home
        else:
            # اگر احراز هویت ناموفق بود، پیام خطا نمایش داده شود
            return render(request, 'login.html', {'error': 'شماره موبایل یا رمز عبور اشتباه است'})
    return render(request, 'login.html')
# class homeView(ListView):
#     model = post
#     template_name = 'salon/home.html'

# Create your views here.
class UserProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'profile.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user


def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, "my_reservations.html", {"reservations": reservations})