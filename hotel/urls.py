from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('rooms/', views.rooms, name='rooms'),
    path('reservation/', views.reservation, name='reservation'),
    path('events/', views.events, name='events'),
    path('contact/', views.contact, name='contact'),
]