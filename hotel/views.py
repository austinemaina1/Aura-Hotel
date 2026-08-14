from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from reservations.models import Reservation

from rooms.models import Room
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from contact.models import Contact
from reservations.models import Reservation
from reservations.views import sync_room_statuses
from django.contrib.auth.models import Group
from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncMonth

from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

# views for the hotel application
from django.shortcuts import render

def home(request):
    return render(
        request,
        'index.html',
        {'today': timezone.localdate().isoformat()}
    )

def about(request):
    return render(request, 'about.html')

def rooms(request):
    return render(request, 'rooms.html')

from django.utils import timezone

def reservation(request):

    if not request.user.is_authenticated:
        return redirect(
            '/guests/login/?next=/reservation/'
        )

    return render(
        request,
        'reservation.html',
        {
            'today': timezone.localdate().isoformat()
        }
    )

def events(request):
    return render(request, 'events.html')

def contact(request):
    return render(request, 'contact.html')

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')


        user = authenticate(
            request,
            username=username,
            password=password
        )


        if user is not None:

            login(request, user)

            if user.is_superuser:
                return redirect('admin_dashboard')

            elif user.groups.filter(name='Receptionist').exists():
                return redirect('reception_dashboard')

            elif user.groups.filter(name='Housekeeper').exists():
                return redirect('housekeeping_dashboard')

            else:
                return redirect('staff_dashboard')

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

    return render(
        request,
        'login.html'
    )


def logout_view(request):
    logout(request)
    return redirect('home')


from datetime import datetime, date
from django.contrib import messages
from django.shortcuts import redirect
from rooms.models import Room
from reservations.models import Reservation
from datetime import date

def check_availability(request):

    if request.method == 'POST':

        room_type = request.POST.get('room_type')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')

        

        check_in = date.fromisoformat(
            request.POST.get('check_in')
        )

        check_out = date.fromisoformat(
            request.POST.get('check_out')
        )

        today = date.today()

        if check_in < today:
            messages.error(
                request,
                "Check-in date cannot be in the past."
            )
            return redirect('home')

        if check_out <= check_in:
            messages.error(
                request,
                "Check-out date must be after check-in date."
            )
            return redirect('home')

        # All rooms of the selected type
        rooms = Room.objects.filter(
            room_type=room_type,
            status='Available'
        )

        available_room = None

        for room in rooms:

            room_booked = Reservation.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in
            ).exists()

            if not room_booked:
                available_room = room
                break

        if available_room:

            request.session['room_id'] = available_room.id
            request.session['check_in'] = str(check_in)
            request.session['check_out'] = str(check_out)

            messages.success(
                request,
                f"{room_type} room is available."
            )

            return redirect('reservation')

        messages.error(
            request,
            "No rooms available for the selected dates."
        )

        return redirect('home')


from rooms.models import Room
from reservations.models import Reservation
from events.models import Event
from contact.models import Contact

from payments.models import Payment
from reviews.models import Review
from staff.models import Staff
from django.db.models import Sum, Avg


from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum, Avg
from notifications.models import Notification

@login_required
def admin_dashboard(request):

    if not request.user.is_superuser:
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    # Rooms
    total_rooms = Room.objects.count()

    available_rooms = Room.objects.filter(
        status='Available'
    ).count()

    occupied_rooms = Room.objects.filter(
        status='Occupied'
    ).count()

    maintenance_rooms = Room.objects.filter(
        status='Maintenance'
    ).count()

    occupancy_rate = 0

    if total_rooms > 0:
        occupancy_rate = round(
            (occupied_rooms / total_rooms) * 100,
            1
        )

    unread_notifications = Notification.objects.filter(
        is_read=False
    ).count()

    recent_notifications = Notification.objects.order_by(
        '-created_at'
    )[:5]

    # Reservations
    active_reservations = Reservation.objects.filter(
        status__in=[
            'Booked',
            'Checked In',
            'Pending Checkout'
        ]
    ).count()

    today = timezone.now().date()

    this_week_reservations = Reservation.objects.filter(
        created_at__date__gte=today - timedelta(days=7)
    ).count()

    last_week_reservations = Reservation.objects.filter(
        created_at__date__gte=today - timedelta(days=14),
        created_at__date__lt=today - timedelta(days=7)
    ).count()

    if last_week_reservations > 0:
        reservations_trend = round(
            ((this_week_reservations - last_week_reservations)
            / last_week_reservations) * 100,
            1
        )
    elif this_week_reservations > 0:
        reservations_trend = 100
    else:
        reservations_trend = 0


    # Revenue Trend
    this_week_revenue = Payment.objects.filter(
        payment_date__date__gte=today - timedelta(days=7),
        status='Paid'
    ).aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    last_week_revenue = Payment.objects.filter(
        payment_date__date__gte=today - timedelta(days=14),
        payment_date__date__lt=today - timedelta(days=7),
        status='Paid'
    ).aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    if last_week_revenue > 0:
        revenue_trend = round(
            ((this_week_revenue - last_week_revenue)
            / last_week_revenue) * 100,
            1
        )
    elif this_week_revenue > 0:
        revenue_trend = 100
    else:
        revenue_trend = 0


    # Occupancy Trend
    current_occupancy = occupied_rooms

    previous_occupancy = Reservation.objects.filter(
        status='Checked In'
    ).exclude(
        check_in=today
    ).count()

    if previous_occupancy > 0:
        occupancy_trend = round(
            ((current_occupancy - previous_occupancy)
            / previous_occupancy) * 100,
            1
        )
    elif current_occupancy > 0:
        occupancy_trend = 100
    else:
        occupancy_trend = 0




    # Events
    total_events = Event.objects.count()

    # Messages
    total_messages = Contact.objects.count()

    # Payments
    total_payments = Payment.objects.count()

    paid_payments = Payment.objects.filter(
        status='Paid'
    ).count()

    pending_payments = Payment.objects.filter(
        status='Pending'
    ).count()

    total_revenue = Payment.objects.aggregate(
        Sum('amount')
    )['amount__sum'] or 0

        # Revenue Summary Analytics

    today = timezone.now().date()

    revenue_today = Payment.objects.filter(
        payment_date__date=today,
        status='Paid'
    ).aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    week_ago = today - timedelta(days=7)

    revenue_week = Payment.objects.filter(
        payment_date__date__gte=week_ago,
        status='Paid'
    ).aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    revenue_month = Payment.objects.filter(
        payment_date__year=today.year,
        payment_date__month=today.month,
        status='Paid'
    ).aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    # Revenue Analytics

    monthly_revenue = (
        Payment.objects
        .filter(status='Paid')
        .annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    revenue_labels = [
        item['month'].strftime('%b %Y')
        for item in monthly_revenue
    ]

    revenue_data = [
        float(item['total'])
        for item in monthly_revenue
    ]

    # Reservation Analytics

    booked_reservations = Reservation.objects.filter(
        status='Booked'
    ).count()

    checked_in_reservations = Reservation.objects.filter(
        status='Checked In'
    ).count()

    pending_checkout_reservations = Reservation.objects.filter(
        status='Pending Checkout'
    ).count()

    completed_reservations = Reservation.objects.filter(
        status='Completed'
    ).count()

    cancelled_reservations = Reservation.objects.filter(
        status='Cancelled'
    ).count()

    monthly_reservations = (
        Reservation.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

    reservation_labels = [
        item['month'].strftime('%b %Y')
        for item in monthly_reservations
    ]

    reservation_data = [
        item['total']
        for item in monthly_reservations
    ]

    # Reviews
    total_reviews = Review.objects.count()

    average_rating = Review.objects.aggregate(
        Avg('rating')
    )['rating__avg'] or 0

    # Staff
    total_staff = Staff.objects.count()

    management_staff = Staff.objects.filter(
        department='Management'
    ).count()

    reception_staff = Staff.objects.filter(
        department='Reception'
    ).count()

    housekeeping_staff = Staff.objects.filter(
        department='Housekeeping'
    ).count()

    security_staff = Staff.objects.filter(
        department='Security'
    ).count()

    unread_messages = Contact.objects.filter(
    is_read=False
    ).count()

    # Recent Data
    recent_reservations = Reservation.objects.order_by('-id')[:5]
    recent_messages = Contact.objects.order_by('-id')[:5]
    recent_payments = Payment.objects.order_by('-id')[:5]
    recent_reviews = Review.objects.order_by('-created_at')[:5]
    recent_staff = Staff.objects.order_by('-id')[:5]

    cleaning_rooms = 0

    expected_checkins_today = Reservation.objects.filter(
        check_in=today
    ).count()

    checked_in_today = Reservation.objects.filter(
        status='Checked In'
    ).count()

    expected_checkouts_today = Reservation.objects.filter(
        check_out=today
    ).count()

    checked_out_today = Reservation.objects.filter(
        status='Completed'
    ).count()

    rooms_ready = available_rooms
    rooms_cleaning_now = cleaning_rooms
    rooms_occupied_hk = occupied_rooms

    context = {
        'reservations_trend': reservations_trend,
        'revenue_trend': revenue_trend,
        'occupancy_trend': occupancy_trend,

        'active_reservations': active_reservations,
        'revenue_today': revenue_today,
        'revenue_week': revenue_week,
        'revenue_month': revenue_month,

        'booked_reservations': booked_reservations,
        'checked_in_reservations': checked_in_reservations,
        'pending_checkout_reservations': pending_checkout_reservations,
        'completed_reservations': completed_reservations,
        'cancelled_reservations': cancelled_reservations,

        'cleaning_rooms': cleaning_rooms,

        'expected_checkins_today': expected_checkins_today,
        'checked_in_today': checked_in_today,

        'expected_checkouts_today': expected_checkouts_today,
        'checked_out_today': checked_out_today,

        'rooms_ready': rooms_ready,
        'rooms_cleaning_now': rooms_cleaning_now,
        'rooms_occupied_hk': rooms_occupied_hk,



        'unread_messages': unread_messages,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
        'occupancy_rate': occupancy_rate,

            # notifications
        'unread_notifications': unread_notifications,
        'recent_notifications': recent_notifications,

        
        'total_events': total_events,
        'total_messages': total_messages,

        'total_payments': total_payments,
        'paid_payments': paid_payments,
        'pending_payments': pending_payments,
        'total_revenue': total_revenue,

        'revenue_labels': revenue_labels,
        'revenue_data': revenue_data,

        'reservation_labels': reservation_labels,
        'reservation_data': reservation_data,

        'total_reviews': total_reviews,
        'average_rating': average_rating,

        'total_staff': total_staff,
        'management_staff': management_staff,
        'reception_staff': reception_staff,
        'housekeeping_staff': housekeeping_staff,
        'security_staff': security_staff,

        'recent_reservations': recent_reservations,
        'recent_messages': recent_messages,
        'recent_payments': recent_payments,
        'recent_reviews': recent_reviews,
        'recent_staff': recent_staff,
    }

    return render(
        request,
        'dashboard.html',
        context
    )




@login_required
def reception_dashboard(request):

    sync_room_statuses()

    reservations = Reservation.objects.order_by('-id')[:10]

    total_rooms = Room.objects.count()

    available_rooms = Room.objects.filter(
        status='Available'
    ).count()

    occupied_rooms = Room.objects.filter(
        status='Occupied'
    ).count()

    booked_reservations = Reservation.objects.filter(
        status='Booked'
    ).count()

    checked_in_guests = Room.objects.filter(
        status='Occupied'
    ).count()

    total_reservations = Reservation.objects.count()

    today_checkins = Reservation.objects.filter(
        check_in=date.today()
    ).count()

    today_checkouts = Reservation.objects.filter(
        check_out=date.today()
    ).count()

    cleaning_rooms = Room.objects.filter(
    status='Cleaning'
    ).count()

    unread_notifications = Notification.objects.filter(
    is_read=False
    ).count()

    recent_notifications = Notification.objects.order_by(
        '-created_at'
    )[:5]


    context = {
        'reservations': reservations,

        'total_rooms': total_rooms,

        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,

        'total_reservations': total_reservations,

        'today_checkins': today_checkins,
        'today_checkouts': today_checkouts,

        'booked_reservations': booked_reservations,
        'checked_in_guests': checked_in_guests,
        'cleaning_rooms': cleaning_rooms,

        'unread_notifications': unread_notifications,
        'recent_notifications': recent_notifications,
    }

    return render(
        request,
        'reception_dashboard.html',
        context
    )