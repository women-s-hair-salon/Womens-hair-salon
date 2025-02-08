from django.urls import path
from . import views

urlpatterns = [
    path('category/', views.CategoriesView.as_view(), name='categories'),
    path('category/<int:categories_id>/', views.ServicesListView.as_view(), name='services-list'),
    path('category/<int:categories_id>/<int:service_id>/', views.ServicesDetailView.as_view(), name='services-detail'),
    path('category/<int:categories_id>/<int:service_id>/book/', views.BookServiceView.as_view(), name='book-service'),
    path('payment/verify/', views.VerifyPaymentView.as_view(), name='verify-payment'),
]
