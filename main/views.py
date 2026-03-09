from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (
    logout, login as auth_login,
    authenticate, update_session_auth_hash,
    get_user_model,
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse


def home(request):
    from .models import Session
    from datetime import date, timedelta

    today = date.today()
    DAYS_SHORT = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    home_days = []

    for i in range(7):
        d = today + timedelta(days=i)
        sessions = Session.objects.filter(date=d).select_related('coach').order_by('time')
        home_days.append({
            'key':      d.strftime('%Y-%m-%d'),
            'short':    f"{DAYS_SHORT[d.weekday()]} {d.strftime('%d.%m')}",
            'sessions': sessions,
        })

    return render(request, 'main/index.html', {'home_days': home_days})


def contacts(request):
    return render(request, 'main/contacts.html')


def join(request):
    if request.user.is_authenticated:
        return redirect('persacc')

    if request.method == 'POST':
        action = request.POST.get('action')

        # -------- ВХОД --------
        if action == 'login':
            User     = get_user_model()
            email    = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')

            try:
                username = User.objects.get(email=email).username
            except User.DoesNotExist:
                username = email

            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect(request.GET.get('next', 'persacc'))
            else:
                return render(request, 'main/join.html', {
                    'login_error': 'Неверный e-mail или пароль.',
                    'active_tab': 'login',
                })

        # -------- РЕГИСТРАЦИЯ --------
        elif action == 'register':
            User = get_user_model()

            full_name = request.POST.get('full_name', '').strip()
            email     = request.POST.get('email', '').strip()
            phone     = request.POST.get('phone', '').strip()
            role      = request.POST.get('role', 'student')
            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')

            errors = {}
            if not full_name:
                errors['full_name'] = 'Введите имя и фамилию'
            if not email or '@' not in email:
                errors['email'] = 'Введите корректный e-mail'
            elif User.objects.filter(email=email).exists():
                errors['email'] = 'Этот e-mail уже зарегистрирован'
            if len(password1) < 8:
                errors['password1'] = 'Пароль должен содержать минимум 8 символов'
            if password1 != password2:
                errors['password2'] = 'Пароли не совпадают'

            if errors:
                return render(request, 'main/join.html', {
                    'register_errors': errors,
                    'active_tab': 'register',
                    'reg_data': {
                        'full_name': full_name,
                        'email': email,
                        'phone': phone,
                        'role': role,
                    },
                })

            parts      = full_name.split(' ', 1)
            first_name = parts[0]
            last_name  = parts[1] if len(parts) > 1 else ''

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                role=role,
            )

            auth_login(request, user, backend='main.backends.EmailBackend')
            return redirect('persacc')

    return render(request, 'main/join.html', {'active_tab': 'login'})


@login_required(login_url='/join/')
def persacc(request):
    role = getattr(request.user, 'role', 'student')

    if role == 'coach':
        return render(request, 'main/persacc_coach.html')

    elif role == 'admin':
        return render(request, 'main/persacc_admin.html')

    else:
        # Загружаем записи ученика
        from .models import Enrollment
        enrollments = (
            Enrollment.objects
            .filter(student=request.user)
            .select_related('session', 'session__coach')
            .order_by('session__date', 'session__time')
        )
        enrollments_count = enrollments.count()
        trainings_done    = sum(1 for e in enrollments if e.is_past)
        active_days       = enrollments.values('session__date').distinct().count()

        return render(request, 'main/persacc_student.html', {
            'enrollments':       enrollments,
            'enrollments_count': enrollments_count,
            'trainings_done':    trainings_done,
            'active_days':       active_days,
        })


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('home')


def services(request):
    return render(request, 'main/services.html')


def schedule(request):
    from .models import Session, Enrollment
    from datetime import date, timedelta

    today = date.today()
    # Показываем текущую неделю (7 дней начиная с сегодня)
    days_data = []
    DAYS_RU = ['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота','Воскресенье']

    for i in range(7):
        d = today + timedelta(days=i)
        sessions = Session.objects.filter(date=d).select_related('coach').order_by('time')
        days_data.append({
            'key':      d.strftime('%Y-%m-%d'),
            'label':    f"{DAYS_RU[d.weekday()]} {d.strftime('%d.%m')}",
            'sessions': sessions,
        })

    # id тренировок на которые записан текущий пользователь
    enrolled_ids = set()
    if request.user.is_authenticated:
        enrolled_ids = set(
            Enrollment.objects.filter(student=request.user)
            .values_list('session_id', flat=True)
        )

    return render(request, 'main/schedule.html', {
        'days':        days_data,
        'enrolled_ids': enrolled_ids,
    })


@login_required(login_url='/join/')
def enroll(request, session_id):
    """Запись на тренировку."""
    if request.method != 'POST':
        return redirect('schedule')

    from .models import Session, Enrollment
    session = get_object_or_404(Session, id=session_id)

    if session.is_full:
        messages.error(request, 'К сожалению, мест уже нет.')
        return redirect('schedule')

    _, created = Enrollment.objects.get_or_create(
        student=request.user,
        session=session,
    )

    if created:
        messages.success(request, f'Вы записаны на тренировку {session.sport_name} {session.date.strftime("%d.%m")} в {session.time.strftime("%H:%M")}.')
    else:
        messages.error(request, 'Вы уже записаны на эту тренировку.')

    return redirect('schedule')


@login_required(login_url='/join/')
def cancel_enrollment_by_session(request, session_id):
    """Отмена записи прямо из расписания."""
    if request.method != 'POST':
        return redirect('schedule')

    from .models import Session, Enrollment
    session    = get_object_or_404(Session, id=session_id)
    enrollment = Enrollment.objects.filter(student=request.user, session=session).first()

    if enrollment:
        enrollment.delete()
        messages.success(request, 'Запись отменена.')
    else:
        messages.error(request, 'Запись не найдена.')

    return redirect('schedule')


@login_required(login_url='/join/')
def update_profile(request):
    if request.method != 'POST':
        return redirect('persacc')

    user = request.user
    user.first_name = request.POST.get('first_name', '').strip()
    user.last_name  = request.POST.get('last_name', '').strip()
    user.email      = request.POST.get('email', '').strip()
    user.save()

    messages.success(request, 'Профиль успешно обновлён.')
    return redirect('persacc')


@login_required(login_url='/join/')
def change_password(request):
    if request.method != 'POST':
        return redirect('persacc')

    user = request.user
    old_password  = request.POST.get('old_password', '')
    new_password1 = request.POST.get('new_password1', '')
    new_password2 = request.POST.get('new_password2', '')

    if not user.check_password(old_password):
        messages.error(request, 'Неверный текущий пароль.')
        return redirect('persacc')
    if new_password1 != new_password2:
        messages.error(request, 'Пароли не совпадают.')
        return redirect('persacc')
    if len(new_password1) < 8:
        messages.error(request, 'Пароль должен содержать не менее 8 символов.')
        return redirect('persacc')

    user.set_password(new_password1)
    user.save()
    update_session_auth_hash(request, user)
    messages.success(request, 'Пароль успешно изменён.')
    return redirect('persacc')


@login_required(login_url='/join/')
def cancel_enrollment(request, enrollment_id):
    if request.method != 'POST':
        return redirect('persacc')

    from .models import Enrollment
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    enrollment.delete()
    return JsonResponse({'status': 'ok'})