from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Session, Enrollment, RecurringSession, Location


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Роль', {'fields': ('role',)}),
    )
    list_display  = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter   = ('role', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(RecurringSession)
class RecurringSessionAdmin(admin.ModelAdmin):
    list_display  = ('__str__', 'sport', 'coach', 'weekday', 'time', 'date_from', 'date_until', 'is_active')
    list_filter   = ('sport', 'weekday', 'is_active', 'coach')
    actions       = ['generate_sessions_action']

    def generate_sessions_action(self, request, queryset):
        total = sum(r.generate_sessions() for r in queryset)
        self.message_user(request, f'Создано {total} тренировок.')
    generate_sessions_action.short_description = 'Сгенерировать тренировки на 8 недель'


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display   = ('__str__', 'sport', 'coach', 'location', 'date', 'time', 'enrolled_count', 'max_places', 'is_full', 'recurring')
    list_filter    = ('sport', 'date', 'coach')
    search_fields  = ('location', 'coach__first_name', 'coach__last_name')
    date_hierarchy = 'date'
    ordering       = ('date', 'time')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display  = ('student', 'session', 'created_at', 'is_past')
    list_filter   = ('session__sport', 'session__date')
    search_fields = ('student__first_name', 'student__last_name', 'student__email')
    raw_id_fields = ('student', 'session')
    ordering      = ('-created_at',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display  = ('name', 'capacity', 'is_active')
    list_filter   = ('is_active',)
    search_fields = ('name',)