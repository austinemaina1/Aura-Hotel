from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact, name='contact'),
    path('success/', views.contact_success, name='contact_success'),
    path('management/messages/', views.messages_list, name='messages_list'),
    path('management/messages/<int:pk>/', views.message_detail, name='message_detail'),
    path('management/messages/delete/<int:pk>/', views.delete_message, name='delete_message'),
]