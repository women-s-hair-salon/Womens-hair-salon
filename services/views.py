import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views import View
from accounts.models import CustomUser
from .forms import ReservationForm
from django.contrib import messages
from .models import Categories,Service,Reservation
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import DetailView,UpdateView,ListView

class CategoriesView(ListView):
    model =Categories
    template_name = 'categories.html'
    context_object_name = 'categories'
class ServicesListView(ListView):
    model =Service
    template_name = 'services.html'
    context_object_name = 'services'
class ServicesDetailView(DetailView):
    model =Service
    template_name = 'services_detail.html'
    context_object_name = 'services'


ZARINPAL_MERCHANT_ID = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
ZARINPAL_REQUEST_URL = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZARINPAL_VERIFY_URL = "https://api.zarinpal.com/pg/v4/payment/verify.json"
CALLBACK_URL = "http://127.0.0.1:8000/payment/verify/"

class BookServiceView(LoginRequiredMixin, View):
    def post(self, request, categories_id, service_id):
        user = request.user
        date = request.POST.get("date")
        time = request.POST.get("time")

        service = get_object_or_404(Service, id=service_id)

        data = {
            "merchant_id": ZARINPAL_MERCHANT_ID,
            "amount": int(service.price) * 10,  # Convert to Toman
            "description": f"Booking for {service.name}",
            "callback_url": f"{CALLBACK_URL}?user_id={user.id}&service_id={service.id}&date={date}&time={time}",
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(ZARINPAL_REQUEST_URL, json=data, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            if response_data["data"]["code"] == 100:
                authority = response_data["data"]["authority"]
                return redirect(f"https://www.zarinpal.com/pg/StartPay/{authority}")
            else:
                messages.error(request, "Error requesting payment.")
        else:
            messages.error(request, "Error connecting to Zarinpal.")

        return redirect("services-detail", categories_id=categories_id, service_id=service_id)

class VerifyPaymentView(View):
    def get(self, request):
        authority = request.GET.get("Authority")
        status = request.GET.get("Status")

        if status != "OK":
            messages.error(request, "Payment was canceled.")
            return redirect("categories")

        user_id = request.GET.get("user_id")
        service_id = request.GET.get("service_id")
        date = request.GET.get("date")
        time = request.GET.get("time")

        service = get_object_or_404(Service, id=service_id)
        user = get_object_or_404(CustomUser, id=user_id)

        data = {
            "merchant_id": ZARINPAL_MERCHANT_ID,
            "amount": int(service.price) * 10,
            "authority": authority,
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(ZARINPAL_VERIFY_URL, json=data, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            if response_data["data"]["code"] == 100:
                Reservation.objects.create(user=user, service=service, date=date, time=time)
                messages.success(request, "Payment successful! Your reservation is confirmed.")
                return redirect("categories")

        messages.error(request, "Payment verification failed.")
        return redirect("categories")