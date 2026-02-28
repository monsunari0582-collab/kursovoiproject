from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('contacts/', views.contacts, name='contacts'),
    path('join/', views.join, name='join'),
    path('persacc/', views.persacc, name='persacc'),
    path('services/', views.services, name='services'),
    path('schedule/', views.schedule, name='schedule'),
]