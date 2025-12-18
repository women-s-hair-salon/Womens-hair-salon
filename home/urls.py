from .views_staff import (
    StaffTutorialCatalogView,
    StaffTutorialCreateView, StaffTutorialUpdateView, StaffTutorialDeleteView,
    StaffLessonCreateView,   StaffLessonUpdateView,   StaffLessonDeleteView,StaffMessageListView, StaffMessageReplyView,
    StaffMessageDeleteView,StaffMessagesDeleteAllView,
)
from django.urls import path
from . import views



urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('aboutus/', views.AboutUsView.as_view(), name='aboutus'),
    path('contact/', views.ContactUsView.as_view(), name='contact'),
    path('servicesss_list/', views.ServiceCategoryListView.as_view(), name='servicesss_list'),
    path("services_detail/<str:slug>/", views.ServiceCategoryDetailView.as_view(), name="service_category_detail"),
    path("tutorials/", views.TutorialListView.as_view(), name="tutorials"),
    path("tutorials/<str:slug>/", views.TutorialDetailView.as_view(), name="tutorial_detail"),

    #       messages
    path("staff/messages/", StaffMessageListView.as_view(), name="staff_messages"),
    path("staff/messages/<int:pk>/reply/", StaffMessageReplyView.as_view(), name="staff_message_reply"),
    path("staff/messages/<int:pk>/del/", StaffMessageDeleteView.as_view(), name="staff_message_delete"),  # ← جدید
    path('staff/messages/delete-all/', StaffMessagesDeleteAllView.as_view(), name='staff_messages_delete_all'),


    #  مدیریت کاتالوگ
    path("staff/catalog/", views.StaffCatalogManageView.as_view(), name="staff_catalog"),
    path("staff/catalog/category/<str:slug>/edit/", views.StaffCategoryUpdateView.as_view(), name="staff_category_edit"),
    path("staff/catalog/service/<int:pk>/edit/", views.StaffServiceItemUpdateView.as_view(), name="staff_serviceitem_edit"),

    #   Tutorial
    path("staff/tutorials/", StaffTutorialCatalogView.as_view(), name="staff_tutorials"),
    path("staff/tutorials/create/",       StaffTutorialCreateView.as_view(),  name="staff_tutorial_create"),
    path("staff/tutorials/<int:pk>/edit/",StaffTutorialUpdateView.as_view(),  name="staff_tutorial_update"),
    path("staff/tutorials/<int:pk>/del/", StaffTutorialDeleteView.as_view(),  name="staff_tutorial_delete"),

    path("staff/tutorials/lesson/create/",        StaffLessonCreateView.as_view(),  name="staff_lesson_create"),
    path("staff/tutorials/lesson/<int:pk>/edit/", StaffLessonUpdateView.as_view(),  name="staff_lesson_update"),
    path("staff/tutorials/lesson/<int:pk>/del/",  StaffLessonDeleteView.as_view(),  name="staff_lesson_delete"),
]