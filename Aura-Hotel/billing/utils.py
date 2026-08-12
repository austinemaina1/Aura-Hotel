from datetime import timedelta
from .models import Invoice

def create_invoice(reservation):

    nights = (
        reservation.check_out -
        reservation.check_in
    ).days

    if nights <= 0:

        nights = 1

    room_rate = reservation.room.price

    room_charge = nights * room_rate

    invoice, created = Invoice.objects.get_or_create(

        reservation=reservation,

        defaults={

            'nights': nights,

            'room_rate': room_rate,

            'room_charge': room_charge,

            'total_amount': room_charge,

        }

    )

    return invoice