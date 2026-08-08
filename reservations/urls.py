from django.urls import path
from . import views

urlpatterns = [
    path(
        'guest-booking/',
        views.guest_booking,
        name='guest_booking'
    ),

    path('', views.reservation_list, name='reservation_list'),
    path('add_reservation/', views.create_reservation, name='create_reservation'),
    path('edit_reservation/<int:id>/', views.edit_reservation, name='edit_reservation'),
    path('delete_reservation/<int:id>/', views.delete_reservation, name='delete_reservation'),
    path('reservation-management/', views.reservation_management, name='reservation_management'),
    path('reservation-success/', views.reservation_success, name='reservation_success'),
    path('room-unavailable/', views.room_unavailable, name='room_unavailable'),
    path(
    'check-in/<int:reservation_id>/',
    views.check_in_guest,
    name='check_in_guest'
    ),

    path(
        'check-out/<int:reservation_id>/',
        views.check_out_guest,
        name='check_out_guest'
    ),
]