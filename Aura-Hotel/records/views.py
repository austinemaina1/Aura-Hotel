from django.shortcuts import render
from .models import AuditLog
from django.http import HttpResponse
from openpyxl import Workbook

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from .models import AuditLog


def records_dashboard(request):

    logs = AuditLog.objects.order_by(
        '-created_at'
    )

    return render(
        request,
        'records_dashboard.html',
        {
            'logs': logs
        }
    )

from django.shortcuts import render
from .models import AuditLog


def audit_dashboard(request):

    logs = AuditLog.objects.all().order_by('-created_at')

    context = {
        'logs': logs,
        'total_logs': logs.count(),
        'checkins': logs.filter(action_type='Check In').count(),
        'payments': logs.filter(action_type='Payment').count(),
        'checkouts': logs.filter(action_type='Check Out').count(),
        'housekeeping': logs.filter(action_type='Housekeeping').count(),
    }

    return render(
        request,
        'audit_dashboard.html',
        context
    )

def export_audit_pdf(request):

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="audit_report.pdf"'

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "Aura Hotel Audit Report",
        styles['Title']
    )

    elements.append(title)
    elements.append(Spacer(1, 20))

    data = [
        [
            'Date',
            'User',
            'Action',
            'Description'
        ]
    ]

    logs = AuditLog.objects.all().order_by(
        '-created_at'
    )

    for log in logs:

        data.append([
            log.created_at.strftime(
                '%d %b %Y %H:%M'
            ),
            log.user.username if log.user else 'System',
            log.action_type,
            log.description
        ])

    table = Table(data)

    table.setStyle(

        TableStyle([

            (
                'BACKGROUND',
                (0,0),
                (-1,0),
                colors.darkblue
            ),

            (
                'TEXTCOLOR',
                (0,0),
                (-1,0),
                colors.white
            ),

            (
                'GRID',
                (0,0),
                (-1,-1),
                1,
                colors.black
            ),

            (
                'FONTNAME',
                (0,0),
                (-1,0),
                'Helvetica-Bold'
            ),

        ])

    )

    elements.append(table)

    doc.build(elements)

    return response

def export_audit_excel(request):

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = "Audit Logs"

    headers = [
        'Date',
        'User',
        'Action',
        'Description'
    ]

    sheet.append(headers)

    logs = AuditLog.objects.all().order_by(
        '-created_at'
    )

    for log in logs:

        sheet.append([

            log.created_at.strftime(
                '%d %b %Y %H:%M'
            ),

            log.user.username
            if log.user else 'System',

            log.action_type,

            log.description

        ])

    response = HttpResponse(

        content_type=
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename=audit_logs.xlsx'

    workbook.save(response)

    return response

