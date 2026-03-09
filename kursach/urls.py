from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/',                                        admin.site.urls),
    path('',                                              views.home,                         name='home'),
    path('contacts/',                                     views.contacts,                     name='contacts'),
    path('join/',                                         views.join,                         name='join'),
    path('persacc/',                                      views.persacc,                      name='persacc'),
    path('services/',                                     views.services,                     name='services'),
    path('schedule/',                                     views.schedule,                     name='schedule'),
    path('logout/',                                       views.logout_view,                  name='logout'),
    path('update-profile/',                               views.update_profile,               name='update_profile'),
    path('change-password/',                              views.change_password,              name='change_password'),

    # Ученик
    path('enroll/<int:session_id>/',                      views.enroll,                       name='enroll'),
    path('cancel-enrollment/<int:enrollment_id>/',        views.cancel_enrollment,            name='cancel_enrollment'),
    path('cancel-enrollment/session/<int:session_id>/',   views.cancel_enrollment_by_session, name='cancel_enrollment_by_session'),

    # Тренер — тренировки
    path('coach/session/add/',                            views.coach_session_add,            name='coach_session_add'),
    path('coach/session/<int:session_id>/edit/',          views.coach_session_edit,           name='coach_session_edit'),
    path('coach/session/<int:session_id>/delete/',        views.coach_session_delete,         name='coach_session_delete'),
    path('coach/recurring/<int:recurring_id>/delete/',    views.coach_recurring_delete,       name='coach_recurring_delete'),

    # Тренер — ученики
    path('coach/student/<int:student_id>/remove/',        views.coach_student_remove,         name='coach_student_remove'),
]