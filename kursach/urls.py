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
    path('logout/', views.logout_view, name='logout'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('cancel-enrollment/<int:enrollment_id>/', views.cancel_enrollment, name='cancel_enrollment'),
]