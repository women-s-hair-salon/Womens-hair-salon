from django.shortcuts import render,redirect
from django.views.generic.list import ListView
from .models import post
from django.contrib.auth import authenticate, login
from .forms import CustomUserCreationForm

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
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

def home_view(request):
    return render(request, 'home.html')