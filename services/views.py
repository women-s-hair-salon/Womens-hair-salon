from services.models import Service, TimeSlot, Reservation
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
import json
from datetime import datetime

# صفحه اصلی رزرو (فقط برای نمایش اولیه فرم)
class ReservationView(LoginRequiredMixin, TemplateView):
    template_name = 'reservation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_completed'] = self.request.user.is_completed
        return context

# API دریافت سرویس‌ها برای Alpine
class ServiceListView(LoginRequiredMixin, View):
    def get(self, request):
        services = Service.objects.all()
        data = [{'id': s.id, 'name': s.name, 'deposit': s.deposit} for s in services]
        return JsonResponse(data, safe=False)



# API دریافت تایم‌های رزرو شده و آزاد
class TimeSlotListView(LoginRequiredMixin, View):
    def get(self, request):
        service_id = request.GET.get('service')
        date_str = request.GET.get('date')
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

        slots = TimeSlot.objects.filter(service_id=service_id, date=date_obj)
        reserved_slots = Reservation.objects.filter(slot__in=slots).values_list('slot_id', flat=True)

        data = []
        for slot in slots:
            data.append({
                'id': slot.id,
                'time': slot.time.strftime("%H:%M"),
                'isBooked': slot.id in reserved_slots
            })
        return JsonResponse(data, safe=False)

class CreateReservationView(LoginRequiredMixin, View):
    def post(self, request):
        import json
        data = json.loads(request.body)
        service_id = data.get('service_id')
        slot_id = data.get('slot_id')

        try:
            service = Service.objects.get(id=service_id)
            slot = TimeSlot.objects.get(id=slot_id, service=service)
        except (Service.DoesNotExist, TimeSlot.DoesNotExist):
            return HttpResponseBadRequest("Invalid service or slot")

        if Reservation.objects.filter(slot=slot).exists():
            return HttpResponseBadRequest("Slot already booked")

        reservation = Reservation.objects.create(
            user=request.user,
            service=service,
            slot=slot,
            is_paid=False
        )

        # در اینجا بعداً به درگاه پرداخت وصل می‌شویم
        return JsonResponse({'reservation_id': reservation.id, 'payment_url': '/mock-payment/'})

# class ReservationStepOneView(LoginRequiredMixin, View):
#     def get(self, request):
#         services = Service.objects.all()
#         return render(request, 'step_one.html', {
#             'services': services
#         })
#
#
# class ReservationStepTwoView(LoginRequiredMixin, View):
#
#     def post(self, request):
#         service_id = request.POST.get("service_id")
#         date_str = request.POST.get("date")
#
#         try:
#             service = Service.objects.get(pk=service_id)
#             selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#         except (Service.DoesNotExist, ValueError, TypeError):
#             return JsonResponse({"success": False, "message": "داده نامعتبر."}, status=400)
#
#         start_hour = 8
#         end_hour = 20
#         slots = []
#         duration = service.duration_minutes
#
#         current_time = time(hour=start_hour)
#         while datetime.combine(selected_date, current_time) + timedelta(minutes=duration) <= datetime.combine(selected_date, time(hour=end_hour)):
#             start_dt_naive = datetime.combine(selected_date, current_time)
#             end_dt_naive = start_dt_naive + timedelta(minutes=duration)
#
#             start_dt = make_tehran_aware(start_dt_naive)
#             end_dt = make_tehran_aware(end_dt_naive)
#
#             conflict = Reservation.objects.filter(
#                 start_datetime__lt=end_dt,
#                 end_datetime__gt=start_dt,
#                 status='reserved'
#             ).exists() or TimeBlock.objects.filter(
#                 date=selected_date,
#                 start_time__lt=end_dt.time(),
#                 end_time__gt=start_dt.time()
#             ).exists()
#
#             slots.append({
#                 'start': start_dt.strftime('%H:%M'),
#                 'end': end_dt.strftime('%H:%M'),
#                 'available': not conflict and start_dt > timezone.localtime()
#             })
#
#             current_time = (datetime.combine(date.today(), current_time) + timedelta(minutes=duration)).time()
#         print("تاریخ انتخاب‌شده:", selected_date, "تعداد تایم‌ها:", len(slots))
#
#         return JsonResponse({
#             'success': True,
#             'service_id': service_id,
#             'date': date_str,
#             'slots': slots
#         })
#
#
# class ReservationConfirmView(LoginRequiredMixin, View):
#     def post(self, request):
#         user = request.user
#         if not user.first_name or not user.last_name or not user.birthday:
#             return JsonResponse({"success": False, "message": "ابتدا پروفایل خود را کامل کنید."}, status=400)
#
#         service_id = request.POST.get("service_id")
#         date_str = request.POST.get("date")
#         start_str = request.POST.get("start_time")
#
#         try:
#             service = Service.objects.get(pk=service_id)
#             date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
#             start_time_obj = datetime.strptime(start_str, "%H:%M").time()
#         except Exception:
#             return JsonResponse({"success": False, "message": "داده نادرست است."}, status=400)
#
#         start_dt_naive = datetime.combine(date_obj, start_time_obj)
#         end_dt_naive = start_dt_naive + timedelta(minutes=service.duration_minutes)
#
#         start_dt = make_tehran_aware(start_dt_naive)
#         end_dt = make_tehran_aware(end_dt_naive)
#
#         conflict = Reservation.objects.filter(
#             start_datetime__lt=end_dt,
#             end_datetime__gt=start_dt,
#             status='reserved'
#         ).exists() or TimeBlock.objects.filter(
#             date=date_obj,
#             start_time__lt=end_dt.time(),
#             end_time__gt=start_dt.time()
#         ).exists()
#
#         if conflict:
#             return JsonResponse({"success": False, "message": "بازه زمانی قابل رزرو نیست."}, status=400)
#
#         reservation = Reservation.objects.create(
#             user=user,
#             service=service,
#             start_datetime=start_dt,
#             end_datetime=end_dt,
#             deposit_amount=service.deposit_amount,
#             is_paid=False
#         )
#
#         return JsonResponse({
#             "success": True,
#             "message": "در حال انتقال به پرداخت",
#             "redirect_url": f"/pay/redirect/{reservation.id}/"
#         })
#
#
#
# def convert_jalali_to_gregorian(request):
#     jalali = request.GET.get("jalali")
#     try:
#         parts = list(map(int, jalali.split('/')))
#         jd = jdatetime.date(parts[0], parts[1], parts[2])
#         gregorian_date = jd.togregorian()
#         return JsonResponse({'gregorian': gregorian_date.strftime('%Y-%m-%d')})
#     except:
#         return JsonResponse({'error': 'فرمت نادرست'}, status=400)


# class AvailableSlotsView(View):
#     def get(self, request):
#         service_id = request.GET.get('service_id')
#         date_str = request.GET.get('date')  # قالب: YYYY-MM-DD
#
#         if not service_id or not date_str:
#             return JsonResponse({'error': 'اطلاعات ناقص'}, status=400)
#
#         try:
#             selected_service = Service.objects.get(id=service_id)
#             duration_minutes = selected_service.duration_minutes
#         except Service.DoesNotExist:
#             return JsonResponse({'error': 'خدمت موردنظر یافت نشد'}, status=404)
#
#         date = datetime.strptime(date_str, "%Y-%m-%d").date()
#         start_of_day = time(8, 0)
#         end_of_day = time(20, 0)
#
#         existing_appointments = Appointment.objects.filter(date=date)
#         blocked_slots = BlockedTime.objects.filter(date=date)
#
#         unavailable = []
#         for r in existing_appointments:
#             unavailable.append((r.start_time, r.end_time))
#         for b in blocked_slots:
#             unavailable.append((b.start_time, b.end_time))
#
#         def is_slot_available(start):
#             end = (datetime.combine(date, start) + timedelta(minutes=duration_minutes)).time()
#             if end > end_of_day:
#                 return False
#             for u_start, u_end in unavailable:
#                 if not (end <= u_start or start >= u_end):
#                     return False
#             return True
#
#         slots = []
#         current = start_of_day
#         while (datetime.combine(date, current) + timedelta(minutes=duration_minutes)).time() <= end_of_day:
#             if is_slot_available(current):
#                 end = (datetime.combine(date, current) + timedelta(minutes=duration_minutes)).time()
#                 slots.append({
#                     'start': current.strftime('%H:%M'),
#                     'end': end.strftime('%H:%M'),
#                     'duration': f"{duration_minutes // 60} ساعت" if duration_minutes >= 60 else f"{duration_minutes} دقیقه"
#                 })
#             current_dt = datetime.combine(date, current) + timedelta(minutes=15)
#             current = current_dt.time()
#
#         return JsonResponse({'slots': slots})


# from django.views import View
# from django.http import JsonResponse
# from django.utils.timezone import localtime
# from datetime import datetime, timedelta, time
# from .models import Appointment, BlockedTime
# from .choices import SERVICE_DURATIONS
# import jdatetime
#
# class AvailableTimeView(View):
#     def get(self, request):
#         service_type = request.GET.get("service")
#         date_str = request.GET.get("date")
#
#         if not service_type or not date_str:
#             return JsonResponse({"success": False, "error": "پارامترهای لازم ارسال نشده‌اند."}, status=400)
#
#         try:
#             j_date = jdatetime.datetime.strptime(date_str, "%Y-%m-%d").date()
#             g_date = j_date.togregorian()
#         except ValueError:
#             return JsonResponse({"success": False, "error": "فرمت تاریخ معتبر نیست."}, status=400)
#
#         service_duration = SERVICE_DURATIONS.get(service_type)
#         if not service_duration:
#             return JsonResponse({"success": False, "error": "نوع خدمات نامعتبر است."}, status=400)
#
#         work_start = time(8, 0)
#         work_end = time(20, 0)
#         slot_duration = timedelta(minutes=service_duration)
#
#         current_time = datetime.combine(g_date, work_start)
#         end_of_day = datetime.combine(g_date, work_end)
#
#         available_slots = []
#
#         while current_time + slot_duration <= end_of_day:
#             start_time = current_time.time()
#             end_time = (current_time + slot_duration).time()
#
#             has_block = BlockedTime.objects.filter(
#                 date=g_date,
#                 start_time__lt=end_time,
#                 end_time__gt=start_time
#             ).exists()
#
#             has_reserve = Appointment.objects.filter(
#                 date=g_date,
#                 start_time__lt=end_time,
#                 end_time__gt=start_time
#             ).exists()
#
#             if not has_block and not has_reserve:
#                 available_slots.append({
#                     "start": start_time.strftime("%H:%M"),
#                     "end": end_time.strftime("%H:%M")
#                 })
#
#             current_time += timedelta(minutes=30)
#
#         return JsonResponse({
#             "success": True,
#             "slots": available_slots
#         })
#



# import requests
# from django.shortcuts import render, redirect, get_object_or_404
# from django.conf import settings
# from django.views import View
# from accounts.models import CustomUser
# from .forms import ReservationForm
# from django.contrib import messages
# from .models import Categories,Service,Reservation
# from django.contrib.auth.mixins import LoginRequiredMixin
#
# from django.views.generic import DetailView,UpdateView,ListView
#
# class CategoriesView(ListView):
#     model =Categories
#     template_name = 'categories.html'
#     context_object_name = 'categories'
#
#
# class ServicesListView(ListView):
#     model =Service

#     context_object_name = 'services'
#
#
# class ServicesDetailView(DetailView):
#     model =Service
#     template_name = 'services_detail.html'
#     context_object_name = 'services'
#
#
# ZARINPAL_MERCHANT_ID = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
# ZARINPAL_REQUEST_URL = "https://api.zarinpal.com/pg/v4/payment/request.json"
# ZARINPAL_VERIFY_URL = "https://api.zarinpal.com/pg/v4/payment/verify.json"
# CALLBACK_URL = "http://127.0.0.1:8000/payment/verify/"
#
# class BookServiceView(LoginRequiredMixin, View):
#     def post(self, request, categories_id, service_id):
#         user = request.user
#         date = request.POST.get("date")
#         time = request.POST.get("time")
#
#         service = get_object_or_404(Service, id=service_id)
#
#         data = {
#             "merchant_id": ZARINPAL_MERCHANT_ID,
#             "amount": int(service.price) * 10,  # Convert to Toman
#             "description": f"Booking for {service.name}",
#             "callback_url": f"{CALLBACK_URL}?user_id={user.id}&service_id={service.id}&date={date}&time={time}",
#         }
#
#         headers = {"Content-Type": "application/json"}
#         response = requests.post(ZARINPAL_REQUEST_URL, json=data, headers=headers)
#
#         if response.status_code == 200:
#             response_data = response.json()
#             if response_data["data"]["code"] == 100:
#                 authority = response_data["data"]["authority"]
#                 return redirect(f"https://www.zarinpal.com/pg/StartPay/{authority}")
#             else:
#                 messages.error(request, "Error requesting payment.")
#         else:
#             messages.error(request, "Error connecting to Zarinpal.")
#
#         return redirect("services-detail", categories_id=categories_id, service_id=service_id)
#
# class VerifyPaymentView(View):
#     def get(self, request):
#         authority = request.GET.get("Authority")
#         status = request.GET.get("Status")
#
#         if status != "OK":
#             messages.error(request, "Payment was canceled.")
#             return redirect("categories")
#
#         user_id = request.GET.get("user_id")
#         service_id = request.GET.get("service_id")
#         date = request.GET.get("date")
#         time = request.GET.get("time")
#
#         service = get_object_or_404(Service, id=service_id)
#         user = get_object_or_404(CustomUser, id=user_id)
#
#         data = {
#             "merchant_id": ZARINPAL_MERCHANT_ID,
#             "amount": int(service.price) * 10,
#             "authority": authority,
#         }
#
#         headers = {"Content-Type": "application/json"}
#         response = requests.post(ZARINPAL_VERIFY_URL, json=data, headers=headers)
#
#         if response.status_code == 200:
#             response_data = response.json()
#             if response_data["data"]["code"] == 100:
#                 Reservation.objects.create(user=user, service=service, date=date, time=time)
#                 messages.success(request, "Payment successful! Your reservation is confirmed.")
#                 return redirect("categories")
#
#         messages.error(request, "Payment verification failed.")
#         return redirect("categories")