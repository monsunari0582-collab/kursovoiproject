from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (
    logout, login as auth_login,
    authenticate, update_session_auth_hash,
    get_user_model,
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse


# ── декоратор: только для тренеров ──────────────────────────
def coach_required(view_func):
    @login_required(login_url='/join/')
    def wrapper(request, *args, **kwargs):
        if getattr(request.user, 'role', None) != 'coach':
            return redirect('persacc')
        return view_func(request, *args, **kwargs)
    return wrapper


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
        from .models import Session, Enrollment
        from datetime import date, timedelta

        today = date.today()
        DAYS_SHORT = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        coach_days = []

        for i in range(7):
            d = today + timedelta(days=i)
            sessions = (
                Session.objects
                .filter(coach=request.user, date=d)
                .prefetch_related('enrollments__student')
                .order_by('time')
            )
            coach_days.append({
                'key':      d.strftime('%Y-%m-%d'),
                'short':    f"{DAYS_SHORT[d.weekday()]} {d.strftime('%d.%m')}",
                'date':     d,
                'sessions': sessions,
            })

        # Все ученики тренера (записанные на любую его тренировку)
        User = get_user_model()
        student_ids = (
            Enrollment.objects
            .filter(session__coach=request.user)
            .values_list('student_id', flat=True)
            .distinct()
        )
        students_qs = User.objects.filter(id__in=student_ids)

        def ru_zapisey(n):
            if 11 <= (n % 100) <= 19:
                return f"{n} записей"
            r = n % 10
            if r == 1: return f"{n} запись"
            if 2 <= r <= 4: return f"{n} записи"
            return f"{n} записей"

        students = []
        for s in students_qs:
            count = Enrollment.objects.filter(student=s, session__coach=request.user).count()
            students.append({'user': s, 'enrollments_str': ru_zapisey(count)})

        total_sessions   = Session.objects.filter(coach=request.user).count()
        total_students   = len(students)
        weekly_sessions  = Session.objects.filter(
            coach=request.user,
            date__gte=today,
            date__lt=today + timedelta(days=7)
        ).count()

        return render(request, 'main/persacc_coach.html', {
            'coach_days':      coach_days,
            'students':        students,
            'total_sessions':  total_sessions,
            'total_students':  total_students,
            'weekly_sessions': weekly_sessions,
        })

    elif role == 'admin':
        return render(request, 'main/persacc_admin.html')

    else:
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
    days_data = []
    DAYS_RU = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

    for i in range(7):
        d = today + timedelta(days=i)
        sessions = Session.objects.filter(date=d).select_related('coach').order_by('time')
        days_data.append({
            'key':      d.strftime('%Y-%m-%d'),
            'label':    f"{DAYS_RU[d.weekday()]} {d.strftime('%d.%m')}",
            'sessions': sessions,
        })

    enrolled_ids = set()
    if request.user.is_authenticated:
        enrolled_ids = set(
            Enrollment.objects.filter(student=request.user)
            .values_list('session_id', flat=True)
        )

    return render(request, 'main/schedule.html', {
        'days':         days_data,
        'enrolled_ids': enrolled_ids,
    })


@login_required(login_url='/join/')
def enroll(request, session_id):
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
        messages.success(request, f'Вы записаны: {session.sport_name} {session.date.strftime("%d.%m")} в {session.time.strftime("%H:%M")}.')
    else:
        messages.error(request, 'Вы уже записаны на эту тренировку.')

    return redirect('schedule')


@login_required(login_url='/join/')
def cancel_enrollment_by_session(request, session_id):
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


# ══════════════════════════════════════════════
#  ТРЕНЕР — управление тренировками
# ══════════════════════════════════════════════

@coach_required
def coach_session_add(request):
    """Добавить разовую или повторяющуюся тренировку."""
    if request.method != 'POST':
        return redirect('persacc')

    from .models import Session, RecurringSession
    sport      = request.POST.get('sport', '').strip()
    location   = request.POST.get('location', '').strip()
    time_str   = request.POST.get('time', '').strip()
    duration   = int(request.POST.get('duration', 60))
    max_places = int(request.POST.get('max_places', 15))
    repeat     = request.POST.get('repeat', 'once')  # 'once' или 'weekly'

    if not all([sport, location, time_str]):
        messages.error(request, 'Заполните все обязательные поля.')
        return redirect('persacc')

    if repeat == 'weekly':
        # Повторяющаяся тренировка
        weekday    = request.POST.get('weekday', '0')
        date_from  = request.POST.get('date_from', '').strip()
        date_until = request.POST.get('date_until', '').strip() or None

        if not date_from:
            messages.error(request, 'Укажите дату начала.')
            return redirect('persacc')

        rec = RecurringSession.objects.create(
            sport=sport,
            coach=request.user,
            location=location,
            weekday=int(weekday),
            time=time_str,
            duration=duration,
            max_places=max_places,
            date_from=date_from,
            date_until=date_until,
        )
        count = rec.generate_sessions(weeks_ahead=8)
        messages.success(request, f'Создано {count} тренировок по расписанию.')

    else:
        # Разовая тренировка
        date_str = request.POST.get('date', '').strip()
        if not date_str:
            messages.error(request, 'Укажите дату.')
            return redirect('persacc')

        Session.objects.create(
            sport=sport,
            coach=request.user,
            location=location,
            date=date_str,
            time=time_str,
            duration=duration,
            max_places=max_places,
        )
        messages.success(request, 'Тренировка добавлена.')

    return redirect('persacc')


@coach_required
def coach_recurring_delete(request, recurring_id):
    """Удалить шаблон повторения и все будущие тренировки по нему."""
    if request.method != 'POST':
        return redirect('persacc')

    from .models import RecurringSession
    from datetime import date
    rec = get_object_or_404(RecurringSession, id=recurring_id, coach=request.user)

    # Удаляем только будущие тренировки без записей
    deleted = rec.sessions.filter(date__gte=date.today(), enrollments=None).delete()
    rec.is_active = False
    rec.save()

    return JsonResponse({'status': 'ok'})


@coach_required
def coach_session_edit(request, session_id):
    """Редактировать тренировку."""
    if request.method != 'POST':
        return redirect('persacc')

    from .models import Session
    session = get_object_or_404(Session, id=session_id, coach=request.user)

    session.sport      = request.POST.get('sport', session.sport).strip()
    session.location   = request.POST.get('location', session.location).strip()
    session.date       = request.POST.get('date', str(session.date)).strip()
    session.time       = request.POST.get('time', str(session.time)).strip()
    session.duration   = int(request.POST.get('duration', session.duration))
    session.max_places = int(request.POST.get('max_places', session.max_places))
    session.save()

    messages.success(request, 'Тренировка обновлена.')
    return redirect('persacc')


@coach_required
def coach_session_delete(request, session_id):
    """Удалить тренировку."""
    if request.method != 'POST':
        return redirect('persacc')

    from .models import Session
    session = get_object_or_404(Session, id=session_id, coach=request.user)
    session.delete()

    return JsonResponse({'status': 'ok'})


# ══════════════════════════════════════════════
#  ТРЕНЕР — управление учениками
# ══════════════════════════════════════════════

@coach_required
def coach_student_remove(request, student_id):
    """Исключить ученика — удалить все его записи на тренировки тренера."""
    if request.method != 'POST':
        return redirect('persacc')

    from .models import Enrollment
    User = get_user_model()
    student = get_object_or_404(User, id=student_id, role='student')

    deleted_count, _ = Enrollment.objects.filter(
        student=student,
        session__coach=request.user,
    ).delete()

    return JsonResponse({'status': 'ok', 'deleted': deleted_count})