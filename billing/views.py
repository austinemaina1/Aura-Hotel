from django.shortcuts import render
from .models import Invoice
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import openpyxl
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from records.utils import create_log
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.conf import settings
import os

from .models import Invoice


def billing_dashboard(request):

    invoices = Invoice.objects.select_related(
        'reservation',
        'reservation__room'
    ).order_by('-created_at')

    return render(
        request,
        'billing_dashboard.html',
        {
            'invoices': invoices
        }
    )

from django.shortcuts import render
from django.db.models import Sum

from .models import Invoice


def billing_dashboard(request):

    invoices = Invoice.objects.select_related(
        'reservation',
        'reservation__room'
    ).order_by('-created_at')

    total_revenue = (
        Invoice.objects.aggregate(
            Sum('total_amount')
        )['total_amount__sum'] or 0
    )

    paid_revenue = (
        Invoice.objects.filter(
            status='Paid'
        ).aggregate(
            Sum('total_amount')
        )['total_amount__sum'] or 0
    )

    outstanding_revenue = (
        Invoice.objects.filter(
            status='Pending'
        ).aggregate(
            Sum('total_amount')
        )['total_amount__sum'] or 0
    )

    context = {

        'invoices': invoices,

        'total_revenue': total_revenue,

        'paid_revenue': paid_revenue,

        'outstanding_revenue': outstanding_revenue,

        'total_invoices':
            Invoice.objects.count(),

        'paid_invoices':
            Invoice.objects.filter(
                status='Paid'
            ).count(),

        'pending_invoices':
            Invoice.objects.filter(
                status='Pending'
            ).count(),

    }

    return render(
        request,
        'billing/billing_dashboard.html',
        context
    )

def export_invoice_pdf(request):

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="billing_report.pdf"'

    p = canvas.Canvas(response)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(
        50,
        800,
        "Aura Hotel Billing Report"
    )

    y = 760

    invoices = Invoice.objects.all()

    for invoice in invoices:

        line = (
            f"Invoice #{invoice.id} | "
            f"{invoice.reservation.guest_name} | "
            f"Room {invoice.reservation.room.room_number} | "
            f"KSh {invoice.total_amount} | "
            f"{invoice.status}"
        )

        p.drawString(
            50,
            y,
            line
        )

        y -= 20

        if y < 50:

            p.showPage()
            y = 800

    p.save()

    return response

def export_invoice_excel(request):

    workbook = openpyxl.Workbook()

    sheet = workbook.active

    sheet.title = "Billing Report"

    headers = [

        "Invoice",

        "Guest",

        "Room",

        "Nights",

        "Room Rate",

        "Total",

        "Status",

        "Created"

    ]

    sheet.append(headers)

    invoices = Invoice.objects.all()

    for invoice in invoices:

        sheet.append([

            invoice.id,

            invoice.reservation.guest_name,

            invoice.reservation.room.room_number,

            invoice.nights,

            invoice.room_rate,

            invoice.total_amount,

            invoice.status,

            invoice.created_at.strftime(
                "%d-%m-%Y %H:%M"
            )

        ])

    response = HttpResponse(

        content_type=
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename=billing_report.xlsx'

    workbook.save(response)

    return response

# def invoice_detail(request, invoice_id):

#     invoice = get_object_or_404(
#         Invoice,
#         id=invoice_id
#     )

#     return render(
#         request,
#         'billing/invoice_detail.html',
#         {
#             'invoice': invoice
#         }
#     )

def mark_invoice_paid(request, invoice_id):

    invoice = get_object_or_404(
        Invoice,
        id=invoice_id
    )

    invoice.status = 'Paid'
    invoice.save()

    reservation = invoice.reservation

    reservation.payment_status = 'Paid'
    reservation.save()

    create_log(
        request.user,
        'Payment',
        f'Invoice #{invoice.id} marked paid for '
        f'{reservation.guest_name}'
    )

    messages.success(
        request,
        'Invoice marked as paid.'
    )

    return redirect(
        'invoice_detail',
        invoice_id=invoice.id
    )

def invoice_pdf(request, invoice_id):

    invoice = get_object_or_404(
        Invoice,
        id=invoice_id
    )

    invoice_number = (
        f"INV-{invoice.created_at.year}-"
        f"{invoice.id:05d}"
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = (
        f'attachment; '
        f'filename={invoice_number}.pdf'
    )

    p = canvas.Canvas(
        response,
        pagesize=A4
    )

    width, height = A4

    HOTEL_NAME = "Aura Hotel"
    HOTEL_ADDRESS = "Nairobi, Kenya"
    HOTEL_PHONE = "+254 XXX XXX XXX"
    HOTEL_EMAIL = "info@aurahotel.com"

    logo_path = os.path.join(
        settings.BASE_DIR,
        'hotel',
        'static',
        'images',
        'logo.png'
    )

    if os.path.exists(logo_path):

        p.drawImage(
            logo_path,
            50,
            height - 120,
            width=70,
            height=70,
            preserveAspectRatio=True
        )

    p.setFont(
        "Helvetica-Bold",
        24
    )

    p.drawString(
        140,
        height - 60,
        HOTEL_NAME
    )

    p.setFont(
        "Helvetica",
        10
    )

    p.drawString(
        140,
        height - 80,
        HOTEL_ADDRESS
    )

    p.drawString(
        140,
        height - 95,
        HOTEL_PHONE
    )

    p.drawString(
        140,
        height - 110,
        HOTEL_EMAIL
    )

    y = height - 160

    p.line(
        50,
        y,
        550,
        y
    )

    y -= 30

    p.setFont(
        "Helvetica-Bold",
        14
    )

    p.drawString(
        50,
        y,
        invoice_number
    )

    p.drawString(
        380,
        y,
        f"Date: {invoice.created_at.strftime('%d %b %Y')}"
    )

    y -= 40

    p.setFont(
        "Helvetica-Bold",
        12
    )

    p.drawString(
        50,
        y,
        "Guest Details"
    )

    y -= 20

    p.setFont(
        "Helvetica",
        11
    )

    p.drawString(
        50,
        y,
        f"Name: {invoice.reservation.guest_name}"
    )

    y -= 18

    p.drawString(
        50,
        y,
        f"Email: {invoice.reservation.email}"
    )

    y -= 18

    p.drawString(
        50,
        y,
        f"Phone: {invoice.reservation.phone}"
    )

    y -= 35

    p.setFont(
        "Helvetica-Bold",
        12
    )

    p.drawString(
        50,
        y,
        "Stay Details"
    )

    y -= 20

    p.setFont(
        "Helvetica",
        11
    )

    p.drawString(
        50,
        y,
        f"Room: {invoice.reservation.room.room_number}"
    )

    y -= 18

    p.drawString(
        50,
        y,
        f"Room Type: {invoice.reservation.room.room_type}"
    )

    y -= 18

    p.drawString(
        50,
        y,
        f"Check In: {invoice.reservation.check_in}"
    )

    y -= 18

    p.drawString(
        50,
        y,
        f"Check Out: {invoice.reservation.check_out}"
    )

    y -= 40

    p.line(
        50,
        y,
        550,
        y
    )

    y -= 20

    p.setFont(
        "Helvetica-Bold",
        12
    )

    p.drawString(
        60,
        y,
        "Description"
    )

    p.drawString(
        430,
        y,
        "Amount"
    )

    y -= 15

    p.line(
        50,
        y,
        550,
        y
    )

    y -= 25

    p.setFont(
        "Helvetica",
        11
    )

    p.drawString(
        60,
        y,
        f"Room Charge ({invoice.nights} Nights)"
    )

    p.drawString(
        430,
        y,
        f"KSh {invoice.room_charge}"
    )

    y -= 25

    p.drawString(
        60,
        y,
        "Extra Charges"
    )

    p.drawString(
        430,
        y,
        f"KSh {invoice.extra_charges}"
    )

    y -= 35

    p.line(
        50,
        y,
        550,
        y
    )

    y -= 25

    p.setFont(
        "Helvetica-Bold",
        14
    )

    p.drawString(
        60,
        y,
        "TOTAL"
    )

    p.drawString(
        430,
        y,
        f"KSh {invoice.total_amount}"
    )

    y -= 40

    p.setFont(
        "Helvetica-Bold",
        12
    )

    if invoice.status == 'Paid':

        p.setFillColorRGB(
            0,
            0.5,
            0
        )

    else:

        p.setFillColorRGB(
            0.8,
            0,
            0
        )

    p.drawString(
        60,
        y,
        f"STATUS: {invoice.status}"
    )

    p.setFillColorRGB(
        0,
        0,
        0
    )

    y -= 60

    p.setFont(
        "Helvetica-Oblique",
        10
    )

    p.drawString(
        50,
        y,
        "Thank you for choosing Aura Hotel."
    )

    y -= 15

    p.drawString(
        50,
        y,
        "Generated automatically by Aura Hotel PMS."
    )

    p.save()

    return response

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Invoice


@login_required
def my_invoices(request):

    invoices = Invoice.objects.filter(
        reservation__user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'billing/my_invoices.html',
        {
            'invoices': invoices
        }
    )

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from billing.models import Invoice
from payments.models import Payment


@login_required
def invoice_detail(request, invoice_id):

    if request.user.is_staff or request.user.is_superuser:

        invoice = get_object_or_404(
            Invoice,
            id=invoice_id
        )

    else:

        invoice = get_object_or_404(
            Invoice,
            id=invoice_id,
            reservation__user=request.user
        )

    payment = Payment.objects.filter(
        reservation=invoice.reservation
    ).order_by('-payment_date').first()

    context = {
        'invoice': invoice,
        'payment': payment,
    }

    return render(
        request,
        'billing/invoice_detail.html',
        context
    )
