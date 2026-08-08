from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_list, name='payment_list'),

    path('add_payment/', views.create_payment, name='create_payment'),

    path('edit_payment/<int:id>/', views.edit_payment, name='edit_payment'),

    path('delete_payment/<int:id>/', views.delete_payment, name='delete_payment'),

    path('dashboard/', views.payment_dashboard, name='payment_dashboard'),

    path(
        'make-payment/<int:reservation_id>/',
        views.make_payment,
        name='make_payment'
    ),
]