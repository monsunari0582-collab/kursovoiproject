from django.shortcuts import render

def home(request):
    return render(request, 'main/index.html')

def contacts(request):
    return render(request, 'main/contacts.html')

def join(request):
    return render(request, 'main/join.html')

def persacc(request):
    return render(request, 'main/persacc.html')

def services(request):
    return render(request, 'main/services.html')

def schedule(request):
    return render(request, 'main/schedule.html')

# Create your views here.
