from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    # path('available-slots/', views.AvailableSlotsView.as_view(), name='available_slots'),
    # path('reservation/', views.ReservationStepOneView.as_view(), name='reservation_step_one'),
    # path('reservation/times/', views.ReservationStepTwoView.as_view(), name='reservation_step_two'),
    # path('reservation/confirm/', views.ReservationConfirmView.as_view(), name='reservation_confirm'),
    # path('convert-date/', views.convert_jalali_to_gregorian, name='convert_date'),
    path('reservation/', views.ReservationView.as_view(), name='reservation'),
    path('api/services/', views.ServiceListView.as_view(), name='api_services'),
    path('api/timeslots/', views.TimeSlotListView.as_view(), name='api_timeslots'),
    path('api/create-reservation/', views.CreateReservationView.as_view(), name='create_reservation'),
    path('mock-payment/', TemplateView.as_view(template_name='mock_payment.html'), name='mock_payment'),




    # path('category/<int:categories_id>/', views.ServicesListView.as_view(), name='services-list'),
    # path('category/<int:categories_id>/<int:service_id>/', views.ServicesDetailView.as_view(), name='services-detail'),
    # path('category/<int:categories_id>/<int:service_id>/book/', views.BookServiceView.as_view(), name='book-service'),
    # path('payment/verify/', views.VerifyPaymentView.as_view(), name='verify-payment'),
]
