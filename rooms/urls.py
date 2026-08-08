from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_management, name='room_management'),
    path('add_room/', views.create_room, name='create_room'),
    path('edit_room/<int:id>/', views.edit_room, name='edit_room'),
    path('delete_room/<int:id>/', views.delete_room, name='delete_room'),
    path('room-management/', views.room_management, name='room_management'),

    path(
    'housekeeping/',
    views.housekeeping_dashboard,
    name='housekeeping_dashboard'
    ),

    path(
    'clean-room/<int:room_id>/',
    views.mark_room_clean,
    name='mark_room_clean'
    ),
]