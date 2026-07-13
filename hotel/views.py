from django.shortcuts import render

# views for the hotel application
from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def rooms(request):
    return render(request, 'rooms.html')

def reservation(request):
    return render(request, 'reservation.html')

def events(request):
    return render(request, 'events.html')

def contact(request):
    return render(request, 'contact.html')
