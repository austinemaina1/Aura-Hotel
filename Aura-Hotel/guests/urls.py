from django.urls import path
from . import views

urlpatterns = [

    path(
        'register/',
        views.register_guest,
        name='register_guest'
    ),

    path(
        'login/',
        views.guest_login,
        name='guest_login'
    ),

    path(
        'dashboard/',
        views.guest_dashboard,
        name='guest_dashboard'
    ),

    path(
        'logout/',
        views.logout_user,
        name='logout'
    ),

    path(
    'profile/',
    views.guest_profile,
    name='guest_profile'
    ),

    path(
    'my-reservations/',
    views.my_reservations,
    name='my_reservations'
    ),

    path(
    'cancel-reservation/<int:reservation_id>/',
    views.cancel_reservation,
    name='cancel_reservation'
    ),

    path(
        'leave-review/',
        views.leave_review,
        name='leave_review'
    ),



  
   path(
        'support/',
        views.guest_support,
        name='guest_support'
    ),

]