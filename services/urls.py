
from django.urls import path
from .views import ServiceListView, ChooseDateView, ChooseTimeView, PaymentCallbackView
from .views_staff import (
    StaffStepUpView, StaffLockView, StaffDashboardView,
    StaffUserListView,
    SlotListView, SlotCreateView, SlotUpdateView, SlotDeleteView,BulkSlotCreateView ,
    StaffReservationListView ,
    StaffServiceListView, StaffServiceCreateView, StaffServiceUpdateView,
    StaffServiceDeleteView, StaffServiceToggleActiveView,
)

urlpatterns = [
    path('services/', ServiceListView.as_view(), name='services_list'),  # مثل هدر شما
    path('services/<slug:slug>/date/', ChooseDateView.as_view(), name='choose_date'),
    path('services/<slug:slug>/date/<date>/', ChooseTimeView.as_view(), name='choose_time'),
    path('payment/callback/', PaymentCallbackView.as_view(), name='payment_callback'),

# Staff portal
    path('staff/verify/', StaffStepUpView.as_view(), name='staff_stepup'),
    path('staff/lock/',   StaffLockView.as_view(),  name='staff_lock'),
    path('staff/',        StaffDashboardView.as_view(), name='staff_dashboard'),

    # users
    path('staff/users/',  StaffUserListView.as_view(), name='staff_users'),

    # slots CRUD
    path('staff/slots/',                 SlotListView.as_view(),   name='staff_slots'),
    path('staff/slots/new/',             SlotCreateView.as_view(), name='staff_slot_create'),
    path('staff/slots/<int:pk>/edit/',   SlotUpdateView.as_view(), name='staff_slot_edit'),
    path('staff/slots/<int:pk>/delete/', SlotDeleteView.as_view(), name='staff_slot_delete'),

    path('staff/slots/bulk/', BulkSlotCreateView.as_view(), name='staff_slot_bulk'),

    # services/urls_staff.py یا همان urls
    path('staff/reservations/', StaffReservationListView.as_view(), name='staff_reservations'),


    path('staff/services/', StaffServiceListView.as_view(), name='staff_services'),
    path('staff/services/create/', StaffServiceCreateView.as_view(), name='staff_service_create'),
    path('staff/services/<int:pk>/edit/', StaffServiceUpdateView.as_view(), name='staff_service_edit'),
    path('staff/services/<int:pk>/delete/', StaffServiceDeleteView.as_view(), name='staff_service_delete'),
    path('staff/services/<int:pk>/toggle/', StaffServiceToggleActiveView.as_view(), name='staff_service_toggle'),


]





# from django.urls import path
# from django.views.generic import TemplateView
#




# from . import views
#
# urlpatterns = [
#     # path('available-slots/', views.AvailableSlotsView.as_view(), name='available_slots'),
#     # path('reservation/', views.ReservationStepOneView.as_view(), name='reservation_step_one'),
#     # path('reservation/times/', views.ReservationStepTwoView.as_view(), name='reservation_step_two'),
#     # path('reservation/confirm/', views.ReservationConfirmView.as_view(), name='reservation_confirm'),
#     # path('convert-date/', views.convert_jalali_to_gregorian, name='convert_date'),
#     path('reservation/', views.ReservationView.as_view(), name='reservation'),
#     path('api/services/', views.ServiceListView.as_view(), name='api_services'),
#     path('api/timeslots/', views.TimeSlotListView.as_view(), name='api_timeslots'),
#     path('api/create-reservation/', views.CreateReservationView.as_view(), name='create_reservation'),
#     path('mock-payment/', TemplateView.as_view(template_name='mock_payment.html'), name='mock_payment'),
#
#
#
#
#     # path('category/<int:categories_id>/', views.ServicesListView.as_view(), name='services-list'),
#     # path('category/<int:categories_id>/<int:service_id>/', views.ServicesDetailView.as_view(), name='services-detail'),
#     # path('category/<int:categories_id>/<int:service_id>/book/', views.BookServiceView.as_view(), name='book-service'),
#     # path('payment/verify/', views.VerifyPaymentView.as_view(), name='verify-payment'),
# ]
