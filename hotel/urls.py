from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('rooms/', views.rooms, name='rooms'),
    path('reservation/', views.reservation, name='reservation'),
    path('events/', views.events, name='events'),
    # path('contact/', views.contact, name='contact'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('check-availability/', views.check_availability, name='check_availability'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('reception-dashboard/', views.reception_dashboard, name='reception_dashboard'),

]
