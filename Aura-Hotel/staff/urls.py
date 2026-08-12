from django.urls import path
from . import views

urlpatterns = [

    path('', views.staff_list, name='staff_list'),
    path('add_staff/', views.create_staff, name='create_staff'),
    path('edit_staff/<int:id>/', views.edit_staff, name='edit_staff'),
    path('delete_staff/<int:id>/', views.delete_staff, name='delete_staff'),
    # path('dashboard/', views.staff_dashboard, name='staff_dashboard')
    path(
    'staff-dashboard/',
    views.staff_dashboard,
    name='staff_dashboard'
),
]