from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from requests import request

from .models import Reservation
from .forms import ReservationForm

from rooms.models import Room
from reservations.models import Reservation
from django.contrib import messages
from django.shortcuts import redirect
from notifications.utils import create_notification


def get_available_room(room_type, check_in, check_out):

    rooms = Room.objects.filter(
        room_type=room_type
    ).order_by('room_number')

    for room in rooms:

        conflict = Reservation.objects.filter(
            room=room,
            check_in__lt=check_out,
            check_out__gt=check_in
        ).exists()

        if not conflict:
            return room

    return None


def guest_booking(request):

    if request.method == "POST":

        room_type = request.POST.get('room_type')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')

        room = get_available_room(
            room_type,
            check_in,
            check_out
        )

        if not room:

            messages.error(
                request,
                "No available room for selected dates."
            )

            return redirect('reservation')

        Reservation.objects.create(
            user=request.user,
            guest_name=request.POST.get('guest_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            room=room,
            check_in=check_in,
            check_out=check_out,
            guests=request.POST.get('guests'),
            special_requests=request.POST.get('special_requests'),
            status='Booked'
        )

        return redirect('reservation_success')

    return redirect('home')


def reservation_list(request):
    reservations = Reservation.objects.all()

    return render(
        request,
        'reservation_list.html',
        {'reservations': reservations}
    )


from django.contrib import messages
from django.shortcuts import render, redirect
from rooms.models import Room
from guests.models import GuestProfile
from billing.models import Invoice

def create_reservation(request):

    print("USER:", request.user)
    print("AUTHENTICATED:", request.user.is_authenticated)

    if not request.user.is_authenticated:
        return redirect(
            '/guests/login/?next=/reservation/'
        )

    if request.method == 'POST':

        print("POST RECEIVED")

        form = ReservationForm(request.POST)

        print("FORM VALID?", form.is_valid())
        print("FORM ERRORS:", form.errors)

        if form.is_valid():

            room_id = request.session.get('room_id')

            if not room_id:

                messages.error(
                    request,
                    "Please check room availability first."
                )

                return redirect('home')

            room = Room.objects.get(id=room_id)

            reservation = form.save(commit=False)

            reservation.user = request.user
            reservation.room = room

            reservation.check_in = request.session.get('check_in')
            reservation.check_out = request.session.get('check_out')

            reservation.save()

            create_notification(
            "New Reservation",
            f"{reservation.guest_name} booked Room {reservation.room.room_number}"
        )

            nights = (
                reservation.check_out -
                reservation.check_in
            ).days

            room_charge = (
                reservation.room.price * nights
            )

            Invoice.objects.create(
                reservation=reservation,
                nights=nights,
                room_charge=room_charge,
                extra_charges=0,
                total_amount=room_charge,
                status='Pending'
            )

            profile, created = GuestProfile.objects.get_or_create(
                user=request.user
            )

            if reservation.phone:
                profile.phone_number = reservation.phone

            profile.save()

            request.session.pop('room_id', None)
            request.session.pop('check_in', None)
            request.session.pop('check_out', None)

            return redirect('reservation_success')

        else:

            print("FORM ERRORS:")
            print(form.errors)

    else:

        form = ReservationForm()

    return render(
        request,
        "create_reservation.html",
        {
            "form": form,
            "today": timezone.localdate().isoformat()
        }
        )


@login_required
def edit_reservation(request, id):

    reservation = get_object_or_404(
        Reservation,
        id=id
    )

    if request.method == 'POST':

        form = ReservationForm(
            request.POST,
            instance=reservation
        )

        if form.is_valid():
            form.save()
            return redirect('reservation_list')

    else:

        form = ReservationForm(
            instance=reservation
        )

    return render(
        request,
        'edit_reservation.html',
        {'form': form}
    )


@login_required
def delete_reservation(request, id):

    reservation = get_object_or_404(
        Reservation,
        id=id
    )

    if request.method == 'POST':

        reservation.delete()

        return redirect('reservation_list')

    return render(
        request,
        'delete_reservation.html',
        {'reservation': reservation}
    )

def reservation_success(request):
    return render(request, 'reservation_success.html')



from rooms.models import Room
from reservations.models import Reservation

def reservation_management(request):

    reservations = Reservation.objects.all()

    available_rooms = Room.objects.filter(
        status='Available'
    ).count()

    occupied_rooms = Room.objects.filter(
        status='Occupied'
    ).count()

    booked_reservations = Reservation.objects.filter(
        status='Booked'
    ).count()

    checked_in_guests = Reservation.objects.filter(
        status='Checked In'
    ).count()

    context = {
        'reservations': reservations,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'booked_reservations': booked_reservations,
        'checked_in_guests': checked_in_guests,
    }

    return render(
        request,
        'reservation_management.html',
        context
    )

def room_unavailable(request):
    return render(
        request,
        'room_unavailable.html'
    )

from rooms.models import Room

def sync_room_statuses():

    occupied_room_ids = Reservation.objects.filter(
        status='Checked In'
    ).values_list(
        'room_id',
        flat=True
    )

    for room in Room.objects.all():

        if room.status == 'Maintenance':
            continue

        if room.status == 'Cleaning':
            continue

        if room.id in occupied_room_ids:

            room.status = 'Occupied'

        else:

            room.status = 'Available'

        room.save()



from django.shortcuts import get_object_or_404, redirect
from .models import Reservation
from records.utils import create_log
from billing.utils import create_invoice

def check_in_guest(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    reservation.status = 'Checked In'
    reservation.check_in_time = timezone.now()
    reservation.save()

    create_notification(
    "Guest Checked In",
    f"{reservation.guest_name} checked into Room {reservation.room.room_number}"
    )

    create_invoice(
    reservation
    )

    room = reservation.room

    room.status = 'Occupied'
    room.save()

    create_log(
        request.user,
        'Check In',
        f'{reservation.guest_name} checked into Room {room.room_number}'
    )

    sync_room_statuses()

    return redirect('reservation_management')

from payments.models import Payment

def check_out_guest(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    if request.method == "POST":

        # Receive payment
        if 'receive_payment' in request.POST:

            Payment.objects.create(
                reservation=reservation,
                amount=request.POST.get('amount'),
                payment_method=request.POST.get(
                    'payment_method'
                ),
                transaction_code=request.POST.get(
                    'transaction_code'
                ),
                status='Paid',
                payment_status='Paid'
            )

            reservation.payment_status = 'Paid'
            reservation.save()

            create_notification(
                "Guest Checked Out",
                f"{reservation.guest_name} checked out of Room {room.room_number}"
            )

            create_log(
                request.user,
                'Payment',
                f'Payment received from {reservation.guest_name} for Room {reservation.room.room_number}'
            )

            messages.success(
                request,
                "Payment received successfully."
            )

            return redirect(
                'check_out_guest',
                reservation_id=reservation.id
            )

        # Confirm checkout
        if 'confirm_checkout' in request.POST:

            if reservation.payment_status != 'Paid':

                messages.error(
                    request,
                    "Guest must pay before checkout."
                )

                return redirect(
                    'check_out_guest',
                    reservation_id=reservation.id
                )

            reservation.status = 'Completed'
            reservation.check_out_time = timezone.now()
            reservation.save()

            room = reservation.room
            room.status = 'Cleaning'
            room.save()

            create_log(
    request.user,
    'Check Out',
    f'{reservation.guest_name} checked out of Room {room.room_number}'
                )

            messages.success(
                request,
                "Guest checked out successfully."
            )

            return redirect(
                'reservation_management'
            )

    return render(
        request,
        'checkout_guest.html',
        {
            'reservation': reservation
        }
    )