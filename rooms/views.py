from urllib import request

from django.shortcuts import render, redirect, get_object_or_404

from records.utils import create_log
from .models import Room
from .forms import RoomForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rooms.models import Room
from reservations.models import Reservation


def room_management(request):
    rooms = Room.objects.all()
    return render(request, 'room_management.html', {'rooms': rooms})

@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('room_management')
    else:
        form = RoomForm()

    return render(request, 'create_room.html', {'form': form})

@login_required
def edit_room(request, id):
    room = get_object_or_404(Room, id=id)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('room_management')
    else:
        form = RoomForm(instance=room)

    return render(request, 'edit_room.html', {'form': form})

@login_required
def delete_room(request, id):
    room = get_object_or_404(Room, id=id)

    if request.method == 'POST':
        room.delete()
        return redirect('room_management')

    return render(request, 'delete_room.html', {'room': room})

from .models import Room
from reservations.views import sync_room_statuses

def room_management(request):

    print("=== ROOM MANAGEMENT VIEW EXECUTED ===")

    # Keep room statuses synchronized
    sync_room_statuses()

    rooms = Room.objects.all()

    total_rooms = Room.objects.count()

    occupied_rooms = Reservation.objects.filter(
        status='Checked In'
    ).count()

    booked_reservations = Reservation.objects.filter(
        status='Booked'
    ).count()

    maintenance_rooms = Room.objects.filter(
        status='Maintenance'
    ).count()

    cleaning_rooms = Room.objects.filter(
    status='Cleaning'
    ).count()

    available_rooms = Room.objects.filter(
        status='Available'
    ).count()

    occupancy_rate = 0

    if total_rooms > 0:
        occupancy_rate = round(
            (occupied_rooms / total_rooms) * 100
        )

    # Deluxe Rooms
    deluxe_total = Room.objects.filter(
        room_type='Deluxe'
    ).count()

    deluxe_booked = Room.objects.filter(
        room_type='Deluxe',
        status='Occupied'
    ).count()

    deluxe_available = Room.objects.filter(
        room_type='Deluxe',
        status='Available'
    ).count()

    # Executive Rooms
    executive_total = Room.objects.filter(
        room_type='Executive'
    ).count()

    executive_booked = Room.objects.filter(
        room_type='Executive',
        status='Occupied'
    ).count()

    executive_available = Room.objects.filter(
        room_type='Executive',
        status='Available'
    ).count()

    # Family Suites
    family_total = Room.objects.filter(
        room_type='Family Suite'
    ).count()

    family_booked = Room.objects.filter(
        room_type='Family Suite',
        status='Occupied'
    ).count()

    family_available = Room.objects.filter(
        room_type='Family Suite',
        status='Available'
    ).count()

    context = {
        'rooms': rooms,

        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
        'occupancy_rate': occupancy_rate,
        'cleaning_rooms': cleaning_rooms,
        'booked_reservations': booked_reservations,

        'deluxe_total': deluxe_total,
        'deluxe_available': deluxe_available,
        'deluxe_booked': deluxe_booked,

        'executive_total': executive_total,
        'executive_available': executive_available,
        'executive_booked': executive_booked,

        'family_total': family_total,
        'family_available': family_available,
        'family_booked': family_booked,
    }

    return render(
        request,
        'room_management.html',
        context
    )

from django.shortcuts import render
from .models import Room

@login_required
def housekeeping_dashboard(request):

    cleaning_rooms = Room.objects.filter(
        status='Cleaning'
    )

    maintenance_rooms = Room.objects.filter(
        status='Maintenance'
    ).count()

    cleaning_count = Room.objects.filter(
        status='Cleaning'
    ).count()

    available_rooms = Room.objects.filter(
        status='Available'
    ).count()

    occupied_rooms = Room.objects.filter(
        status='Occupied'
    ).count()

    context = {
        'cleaning_rooms': cleaning_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
        'cleaning_count': cleaning_count,
        'total_rooms': Room.objects.count(),
    }

    return render(
        request,
        'housekeeping_dashboard.html',
        context
    )

from django.shortcuts import get_object_or_404, redirect

@login_required
def mark_room_clean(request, room_id):

    room = get_object_or_404(
        Room,
        id=room_id
    )

    room.status = 'Available'
    room.save()

    create_log(
        request.user,
        'Housekeeping',
        f'{request.user.username} marked Room {room.room_number} clean'
    )

    return redirect(
        'housekeeping_dashboard'
    )
