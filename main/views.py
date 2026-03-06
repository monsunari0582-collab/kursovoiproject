from django.shortcuts import render, redirect
from django.contrib.auth import (
    logout, login as auth_login,
    authenticate, update_session_auth_hash,
    get_user_model,
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def home(request):
    return render(request, 'main/index.html')


def contacts(request):
    return render(request, 'main/contacts.html')


def join(request):
    if request.user.is_authenticated:
        return redirect('persacc')

    if request.method == 'POST':
        action = request.POST.get('action')

        # -------- ВХОД --------
        if action == 'login':
            email    = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')

            # EmailBackend принимает username=email
            user = authenticate(request, username=email, password=password)
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

            if hasattr(user, 'profile') and phone:
                user.profile.phone = phone
                user.profile.save()

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
        return render(request, 'main/persacc_student.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('home')


def services(request):
    return render(request, 'main/services.html')


def schedule(request):
    return render(request, 'main/schedule.html')


@login_required(login_url='/join/')
def update_profile(request):
    if request.method != 'POST':
        return redirect('persacc')

    user = request.user
    user.first_name = request.POST.get('first_name', '').strip()
    user.last_name  = request.POST.get('last_name', '').strip()
    user.email      = request.POST.get('email', '').strip()
    user.save()

    if hasattr(user, 'profile'):
        user.profile.phone = request.POST.get('phone', '').strip()
        user.profile.save()

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
    """Отмена записи на тренировку."""
    if request.method != 'POST':
        return redirect('persacc')
    # from .models import Enrollment
    # enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    # enrollment.delete()
    from django.http import JsonResponse
    return JsonResponse({'statis': 'ок'})