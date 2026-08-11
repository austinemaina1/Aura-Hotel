from django.shortcuts import render, redirect, get_object_or_404

from records.utils import create_log
from .models import Payment
from .forms import PaymentForm
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import json
from django.contrib import messages

def payment_list(request):

    payments = Payment.objects.all()

    return render(
        request,
        'payment_list.html',
        {'payments': payments}
    )


def create_payment(request):

    if request.method == 'POST':

        form = PaymentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('payment_list')

    else:
        form = PaymentForm()

    return render(
        request,
        'create_payment.html',
        {'form': form}
    )


def edit_payment(request, id):

    payment = get_object_or_404(
        Payment,
        id=id
    )

    if request.method == 'POST':

        form = PaymentForm(
            request.POST,
            instance=payment
        )

        if form.is_valid():
            form.save()
            return redirect('payment_list')

    else:

        form = PaymentForm(
            instance=payment
        )

    return render(
        request,
        'edit_payment.html',
        {'form': form}
    )


def delete_payment(request, id):

    payment = get_object_or_404(
        Payment,
        id=id
    )

    if request.method == 'POST':
        payment.delete()
        return redirect('payment_list')

    return render(
        request,
        'delete_payment.html',
        {'payment': payment}
    )


from django.db.models import Sum
from django.shortcuts import render
from .models import Payment
from datetime import datetime, time
from django.utils import timezone


def payment_dashboard(request):

    # Revenue Statistics
    total_revenue = Payment.objects.aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    # Temporary fix
    today = timezone.localdate()

    start_of_day = timezone.make_aware(
        datetime.combine(today, time.min)
    )

    end_of_day = timezone.make_aware(
        datetime.combine(today, time.max)
    )

    today_revenue = Payment.objects.filter(
        payment_date__gte=start_of_day,
        payment_date__lte=end_of_day,
        status='Paid'
    ).aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    # Payment Statistics
    total_payments = Payment.objects.count()

    paid_payments = Payment.objects.filter(
        status='Paid'
    ).count()

    pending_payments = Payment.objects.filter(
        status='Pending'
    ).count()

    # Outstanding Balance
    pending_amount = Payment.objects.filter(
        status='Pending'
    ).aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    # Recent Payments
    recent_payments = Payment.objects.order_by(
        '-payment_date'
    )[:5]

    # Payment Method Statistics
    mpesa_count = Payment.objects.filter(
        payment_method='Mpesa'
    ).count()

    cash_count = Payment.objects.filter(
        payment_method='Cash'
    ).count()

    card_count = Payment.objects.filter(
        payment_method='Card'
    ).count()

    bank_count = Payment.objects.filter(
        payment_method='Bank'
    ).count()

    total_methods = (
        mpesa_count +
        cash_count +
        card_count +
        bank_count
    )

    if total_methods > 0:

        mpesa_percent = round(
            (mpesa_count / total_methods) * 100
        )

        cash_percent = round(
            (cash_count / total_methods) * 100
        )

        card_percent = round(
            (card_count / total_methods) * 100
        )

        bank_percent = round(
            (bank_count / total_methods) * 100
        )

    else:

        mpesa_percent = 0
        cash_percent = 0
        card_percent = 0
        bank_percent = 0

    monthly_revenue = (
        Payment.objects
        .filter(status='Paid')
        .annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    chart_labels = [
        item['month'].strftime('%b %Y')
        for item in monthly_revenue
    ]

    chart_data = [
        float(item['total'])
        for item in monthly_revenue
    ]

    context = {

        'total_revenue': total_revenue,
        'today_revenue': today_revenue,

        'total_payments': total_payments,
        'paid_payments': paid_payments,
        'pending_payments': pending_payments,

        'pending_amount': pending_amount,

        'recent_payments': recent_payments,

        'mpesa_count': mpesa_count,
        'cash_count': cash_count,
        'card_count': card_count,
        'bank_count': bank_count,

        'mpesa_percent': mpesa_percent,
        'cash_percent': cash_percent,
        'card_percent': card_percent,
        'bank_percent': bank_percent,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }

    return render(
        request,
        'payment_dashboard.html',
        context
    )

from django.shortcuts import render, redirect, get_object_or_404
from .forms import PaymentForm
from .models import Payment
from reservations.models import Reservation
from notifications.utils import create_notification
from billing.models import Invoice


def make_payment(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    if reservation.payment_status == 'Paid':
        return redirect('guest_dashboard')

    if request.method == 'POST':

        form = PaymentForm(request.POST)

        if form.is_valid():

            payment = form.save(commit=False)

            payment.reservation = reservation
            payment.status = 'Paid'

            payment.save()

            create_notification(
            "Payment Received",
            f"KSh {request.POST.get('amount')} received from {reservation.guest_name}"
        )

            reservation.payment_status = 'Paid'
            reservation.save()

            invoice = Invoice.objects.filter(
            reservation=reservation
        ).first()

        if invoice:
            invoice.status = 'Paid'
            invoice.save()

            return redirect('payment_receipt',payment.id)

    else:

        form = PaymentForm()

    return render(
        request,
        'make_payment.html',
        {
            'reservation': reservation,
            'form': form
        }
    )


from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect

from reservations.models import Reservation
from billing.models import Invoice

from .mpesa import stk_push


def make_mpesa_payment(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    invoice = get_object_or_404(
        Invoice,
        reservation=reservation
    )

    if request.method == "POST":

        phone_number = request.POST.get(
            "phone_number"
        )

        try:

            response = stk_push(
                phone_number=phone_number,
                amount=invoice.total_amount,
                account_reference=f"INV{invoice.id}",
                transaction_desc=(
                    f"Aura Hotel Invoice "
                    f"{invoice.id}"
                )
            )

            if response.get(
                "ResponseCode"
            ) == "0":

                messages.success(
                    request,
                    (
                        "STK Push sent successfully. "
                        "Check your phone."
                    )
                )

            else:

                messages.error(
                    request,
                    response.get(
                        "errorMessage",
                        "Payment failed."
                    )
                )

        except Exception as e:

            messages.error(
                request,
                str(e)
            )

        return redirect(
            "invoice_detail",
            invoice.id
        )

    return redirect(
        "invoice_detail",
        invoice.id
    )

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def mpesa_callback(request):

    if request.method == "POST":

        data = json.loads(request.body)

        print("========== MPESA CALLBACK ==========")
        print(data)
        print("===================================")

        return JsonResponse({
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        })

    return JsonResponse({
        "message": "Callback endpoint working"
    })


from django.shortcuts import render, get_object_or_404
from .models import Payment


def payment_receipt(request, payment_id):

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )

    return render(
        request,
        'payment_receipt.html',
        {
            'payment': payment
        }
    )