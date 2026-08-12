from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.notification_list,
        name='notification_list'
    ),
    path(
    'delete/<int:notification_id>/',
    views.delete_notification,
    name='delete_notification'
    ),


]