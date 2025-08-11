
from django.urls import path
from . import views
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('aboutus/', views.AboutUsView.as_view(), name='aboutus'),
    path('contact/', views.ContactUsView.as_view(), name='contact'),
    path('services_list/', views.ServiceCategoryListView.as_view(), name='services_list'),
    path('services_detail/<slug:slug>/', views.ServiceCategoryDetailView.as_view(), name='service_category_detail'),
    path('tutorials/', views.TutorialsView.as_view(), name='tutorials'),
]