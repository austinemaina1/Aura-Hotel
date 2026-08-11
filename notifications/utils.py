from .models import Notification

def create_notification(title, message):

    Notification.objects.create(
        title=title,
        message=message
    )