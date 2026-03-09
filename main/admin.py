from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Session, Enrollment


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Роль', {'fields': ('role',)}),
    )
    list_display  = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter   = ('role', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display  = ('__str__', 'sport', 'coach', 'location', 'date', 'time', 'enrolled_count', 'max_places', 'is_full')
    list_filter   = ('sport', 'date', 'coach')
    search_fields = ('location', 'coach__first_name', 'coach__last_name')
    date_hierarchy = 'date'
    ordering      = ('date', 'time')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display  = ('student', 'session', 'created_at', 'is_past')
    list_filter   = ('session__sport', 'session__date')
    search_fields = ('student__first_name', 'student__last_name', 'student__email')
    raw_id_fields = ('student', 'session')
    ordering      = ('-created_at',)