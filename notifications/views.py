from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from .models import Notification


def notification_list(request):

    Notification.objects.filter(
        is_read=False
    ).update(
        is_read=True
    )

    notifications = Notification.objects.order_by(
        '-created_at'
    )

    return render(
        request,
        'notifications/notification_list.html',
        {
            'notifications': notifications
        }
    )

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

def delete_notification(
    request,
    notification_id
):

    notification = get_object_or_404(
        Notification,
        id=notification_id
    )

    notification.delete()

    return redirect(
        'notification_list'
    )

