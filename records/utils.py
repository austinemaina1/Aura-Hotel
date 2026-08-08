from .models import AuditLog


def create_log(
    user,
    action_type,
    description
):

    AuditLog.objects.create(
        user=user,
        action_type=action_type,
        description=description
    )