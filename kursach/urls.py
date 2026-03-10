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

    # Администратор — пользователи
    path('admin-panel/user/<int:user_id>/role/',          views.admin_user_role,              name='admin_user_role'),
    path('admin-panel/user/<int:user_id>/block/',         views.admin_user_block,             name='admin_user_block'),
    path('admin-panel/user/<int:user_id>/delete/',        views.admin_user_delete,            name='admin_user_delete'),

    # Администратор — тренировки
    path('admin-panel/session/<int:session_id>/delete/',  views.admin_session_delete,         name='admin_session_delete'),

    # Администратор — залы
    path('admin-panel/location/add/',                     views.admin_location_add,           name='admin_location_add'),
    path('admin-panel/location/<int:location_id>/edit/',  views.admin_location_edit,          name='admin_location_edit'),
    path('admin-panel/location/<int:location_id>/delete/',views.admin_location_delete,        name='admin_location_delete'),
]