from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'main/index.html')

def contacts(request):
    return render(request, 'main/contacts.html')

def join(request):
    return render(request, 'main/join.html')

@login_required
def persacc(request):
    if request.user.role == 'coach':
        return render(request, 'main/persacc_coach.html')
    elif request.user.role == 'admin':
        return render(request, 'main/persacc_admin.html')
    else:
        return render(request, 'main/persacc_student.html')

def services(request):
    return render(request, 'main/services.html')

def schedule(request):
    return render(request, 'main/schedule.html')

# Create your views here.
