from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate,
    login,
    logout
)
from django.contrib.auth.decorators import login_required
from .forms import GuestRegistrationForm
from django.utils import timezone
from reservations.models import Reservation
from reviews.models import Review
from .models import GuestProfile
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .forms import ProfilePictureForm
from .forms import GuestReviewForm
from .models import GuestProfile
from django.contrib.auth.models import Group

def register_guest(request):

    if request.method == 'POST':

        form = GuestRegistrationForm(request.POST)

        if form.is_valid():

            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )

            guest_group = Group.objects.get(name='Guest')
            user.groups.add(guest_group)

            login(request, user)

            return redirect('/reservation/')

    else:

        form = GuestRegistrationForm()

    return render(
        request,
        'guests/register_guest.html',
        {'form': form}
    )

def guest_login(request):

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

            next_url = request.GET.get('next')

            if next_url:
                return redirect(next_url)

            return redirect(
                'guest_dashboard'
            )

    return render(
        request,
        'guests/guest_login.html'
    )

from billing.models import Invoice
@login_required
def guest_dashboard(request):

    my_reservations = Reservation.objects.filter(
        user=request.user
    )

    reservation_count = my_reservations.count()

    upcoming_stays = my_reservations.filter(
        check_in__gte=timezone.now().date()
    ).count()

    completed_stays = my_reservations.filter(
        check_out__lt=timezone.now().date()
    ).count()

    review_count = Review.objects.filter(
        guest_name=request.user.username
    ).count()

    recent_reservations = my_reservations.order_by(
        '-check_in'
    )[:5]

    profile, created = GuestProfile.objects.get_or_create(
        user=request.user
    )

    my_invoices = Invoice.objects.filter(
    reservation__user=request.user
).order_by('-created_at')[:5]
    
    context = {
        'my_invoices': my_invoices,
        'profile': profile,
        'reservation_count': reservation_count,
        'upcoming_stays': upcoming_stays,
        'completed_stays': completed_stays,
        'review_count': review_count,
        'recent_reservations': recent_reservations,
    }

    return render(
        request,
        'guests/guest_dashboard.html',
        context
    )


def logout_user(request):
    logout(request)
    messages.success(
        request,
        "You have been logged out successfully."
    )
    return redirect('home')

@login_required
def guest_profile(request):

    profile, created = GuestProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':

        form = ProfilePictureForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            return redirect('guest_profile')

    else:

        form = ProfilePictureForm(
            instance=profile
        )

    return render(
        request,
        'guests/profile.html',
        {
            'profile': profile,
            'form': form
        }
    )


@login_required
def my_reservations(request):

    reservations = Reservation.objects.filter(
        user=request.user
    ).order_by('-check_in')

    return render(
        request,
        'guests/my_reservations.html',
        {
            'reservations': reservations,
            'today': timezone.now().date()
        }
    )

@login_required
def cancel_reservation(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        user=request.user
    )

    if reservation.check_in <= timezone.now().date():

        messages.error(
            request,
            "This reservation can no longer be cancelled."
        )

        return redirect(
            'my_reservations'
        )

    if reservation.status == 'Cancelled':

        messages.error(
            request,
            "This reservation is already cancelled."
        )

        return redirect(
            'my_reservations'
        )

    reservation.status = 'Cancelled'
    reservation.save()

    messages.success(
        request,
        "Reservation cancelled successfully."
    )

    return redirect(
        'my_reservations'
    )


@login_required
def update_profile_picture(request):

    guest = request.user.guest

    if request.method == 'POST':

        form = ProfilePictureForm(
            request.POST,
            request.FILES,
            instance=guest
        )

        if form.is_valid():
            form.save()
            return redirect('my_profile')

    else:

        form = ProfilePictureForm(
            instance=guest
        )

    return render(
        request,
        'update_profile_picture.html',
        {'form': form}
    )



@login_required
def leave_review(request):

    if request.method == 'POST':

        form = GuestReviewForm(
            request.POST
        )

        if form.is_valid():

            review = form.save(
                commit=False
            )

            review.guest_name = request.user.username

            review.save()

            return redirect(
                'guest_dashboard'
            )

    else:

        form = GuestReviewForm()

    return render(
        request,
        'guests/leave_review.html',
        {
            'form': form
        }
    )

@login_required
def guest_support(request):

    profile, created = GuestProfile.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        'guests/guest_support.html',
        {
            'profile': profile
        }
    )