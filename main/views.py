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

        from datetime import datetime as dt
        now_time = dt.now().time()

        for i in range(7):
            d = today + timedelta(days=i)
            qs = Session.objects.filter(coach=request.user, date=d).prefetch_related('enrollments__student').order_by('time')
            # Сегодня — скрывать тренировки которые уже закончились
            if d == today:
                qs = qs.filter(time__gte=now_time)
            sessions = qs
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

        from .models import RecurringSession
        # Считаем шаблоны + разовые тренировки (не привязанные к шаблону)
        recurring_count  = RecurringSession.objects.filter(coach=request.user, is_active=True).count()
        onetime_count    = Session.objects.filter(coach=request.user, recurring__isnull=True, date__gte=today).count()
        total_sessions   = recurring_count + onetime_count
        total_students   = len(students)
        weekly_sessions  = Session.objects.filter(
            coach=request.user,
            date__gte=today,
            date__lt=today + timedelta(days=7)
        ).count()

        from .models import Location
        locations = Location.objects.filter(is_active=True).order_by('name')

        return render(request, 'main/persacc_coach.html', {
            'coach_days':      coach_days,
            'students':        students,
            'total_sessions':  total_sessions,
            'total_students':  total_students,
            'weekly_sessions': weekly_sessions,
            'locations':       locations,
        })

    elif role == 'admin':
        ctx = _admin_context(request)
        return render(request, 'main/persacc_admin.html', ctx)

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
        qs = Session.objects.filter(date=d).select_related('coach').order_by('time')
        days_data.append({
            'key':      d.strftime('%Y-%m-%d'),
            'label':    f"{DAYS_RU[d.weekday()]} {d.strftime('%d.%m')}",
            'sessions': qs,
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

        repeat_mode = request.POST.get('repeat_mode', 'weekly')
        rec = RecurringSession.objects.create(
            sport=sport,
            coach=request.user,
            location=location,
            weekday=int(weekday) if repeat_mode == 'weekly' else None,
            repeat_mode=repeat_mode,
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


# ══════════════════════════════════════════════
#  Декоратор: только для администраторов
# ══════════════════════════════════════════════

def admin_required(view_func):
    @login_required(login_url='/join/')
    def wrapper(request, *args, **kwargs):
        if getattr(request.user, 'role', None) != 'admin':
            return redirect('persacc')
        return view_func(request, *args, **kwargs)
    return wrapper


# ══════════════════════════════════════════════
#  ADMIN — persacc view (обновлённый)
# ══════════════════════════════════════════════

def _admin_context(request):
    """Собирает весь контекст для кабинета администратора."""
    from .models import Session, Enrollment, Location

    User = get_user_model()
    all_users  = User.objects.all().order_by('role', 'last_name', 'first_name')
    all_sessions = Session.objects.select_related('coach').order_by('-date', 'time')
    locations  = Location.objects.all()

    total_users       = all_users.count()
    total_students    = all_users.filter(role='student').count()
    total_coaches     = all_users.filter(role='coach').count()
    total_sessions    = all_sessions.count()
    total_enrollments = Enrollment.objects.count()
    total_locations   = locations.count()

    # Статистика по видам спорта
    SPORT_LABELS = {
        'volleyball': 'Волейбол',
        'basketball': 'Баскетбол',
        'football':   'Футбол',
        'fitness':    'Фитнес',
    }
    sport_counts = {}
    for s in Session.objects.values_list('sport', flat=True):
        sport_counts[s] = sport_counts.get(s, 0) + 1
    max_count = max(sport_counts.values(), default=1)

    by_sport = [
        {
            'sport':   sport,
            'label':   SPORT_LABELS.get(sport, sport),
            'count':   count,
            'percent': int(count / max_count * 100),
        }
        for sport, count in sorted(sport_counts.items(), key=lambda x: -x[1])
    ]

    return {
        'all_users':    all_users,
        'all_sessions': all_sessions,
        'locations':    locations,
        'stats': {
            'total_users':       total_users,
            'total_students':    total_students,
            'total_coaches':     total_coaches,
            'total_sessions':    total_sessions,
            'total_enrollments': total_enrollments,
            'total_locations':   total_locations,
            'by_sport':          by_sport,
        },
    }


# ══════════════════════════════════════════════
#  ADMIN — управление пользователями
# ══════════════════════════════════════════════

@admin_required
def admin_user_role(request, user_id):
    """Изменить роль пользователя."""
    if request.method != 'POST':
        return JsonResponse({'error': 'method'}, status=405)

    import json
    User = get_user_model()
    u    = get_object_or_404(User, id=user_id)

    if u == request.user:
        return JsonResponse({'error': 'Нельзя изменить свою роль'}, status=400)

    data = json.loads(request.body)
    role = data.get('role', '')
    if role not in ('student', 'coach', 'admin'):
        return JsonResponse({'error': 'Неверная роль'}, status=400)

    u.role = role
    u.save()
    return JsonResponse({'status': 'ok'})


@admin_required
def admin_user_block(request, user_id):
    """Заблокировать / разблокировать пользователя."""
    if request.method != 'POST':
        return JsonResponse({'error': 'method'}, status=405)

    import json
    User = get_user_model()
    u    = get_object_or_404(User, id=user_id)

    if u == request.user:
        return JsonResponse({'error': 'Нельзя заблокировать себя'}, status=400)

    data = json.loads(request.body)
    u.is_active = bool(data.get('is_active', True))
    u.save()
    return JsonResponse({'status': 'ok'})


@admin_required
def admin_user_delete(request, user_id):
    """Удалить пользователя."""
    if request.method != 'POST':
        return JsonResponse({'error': 'method'}, status=405)

    User = get_user_model()
    u    = get_object_or_404(User, id=user_id)

    if u == request.user:
        return JsonResponse({'error': 'Нельзя удалить себя'}, status=400)

    u.delete()
    return JsonResponse({'status': 'ok'})


# ══════════════════════════════════════════════
#  ADMIN — управление тренировками
# ══════════════════════════════════════════════

@admin_required
def admin_session_delete(request, session_id):
    """Удалить любую тренировку."""
    if request.method != 'POST':
        return JsonResponse({'error': 'method'}, status=405)

    from .models import Session
    session = get_object_or_404(Session, id=session_id)
    session.delete()
    return JsonResponse({'status': 'ok'})


# ══════════════════════════════════════════════
#  ADMIN — управление залами
# ══════════════════════════════════════════════

@admin_required
def admin_location_add(request):
    if request.method != 'POST':
        return redirect('persacc')

    from .models import Location
    name     = request.POST.get('name', '').strip()
    capacity = int(request.POST.get('capacity', 20))

    if not name:
        messages.error(request, 'Введите название зала.')
        return redirect('persacc')

    Location.objects.get_or_create(name=name, defaults={'capacity': capacity})
    messages.success(request, f'Зал «{name}» добавлен.')
    return redirect('persacc')


@admin_required
def admin_location_edit(request, location_id):
    if request.method != 'POST':
        return redirect('persacc')

    from .models import Location
    loc          = get_object_or_404(Location, id=location_id)
    loc.name     = request.POST.get('name', loc.name).strip()
    loc.capacity = int(request.POST.get('capacity', loc.capacity))
    loc.is_active = request.POST.get('is_active', '1') == '1'
    loc.save()

    messages.success(request, 'Зал обновлён.')
    return redirect('persacc')


@admin_required
def admin_location_delete(request, location_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'method'}, status=405)

    from .models import Location
    loc = get_object_or_404(Location, id=location_id)
    loc.delete()
    return JsonResponse({'status': 'ok'})