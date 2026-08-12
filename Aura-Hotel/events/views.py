from django.shortcuts import render, redirect
from .models import Event
from .forms import EventForm
from django.shortcuts import get_object_or_404


# Guest page
def events(request):
    events = Event.objects.all()
    return render(request, 'events/events.html', {'events': events})


# Management page
def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})


def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)

        print("POST DATA:", request.POST)

        if form.is_valid():
            print("FORM IS VALID")
            form.save()
            return redirect('event_list')
        else:
            print("FORM ERRORS:", form.errors)

    else:
        form = EventForm()

    return render(request, 'events/add_event.html', {'form': form})

def edit_event(request, id):
    event = get_object_or_404(Event, id=id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event)

    return render(request, 'events/edit_event.html', {'form': form})

def delete_event(request, id):
    event = get_object_or_404(Event, id=id)

    if request.method == 'POST':
        event.delete()
        return redirect('event_list')

    return render(request, 'events/delete_event.html', {'event': event})