from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.billing_dashboard,
        name='billing_dashboard'
    ),

    path(
        'dashboard/',
        views.billing_dashboard,
        name='billing_dashboard'
    ),

    path(
    'export/pdf/',
    views.export_invoice_pdf,
    name='export_invoice_pdf'
    ),

    path(
        'export/excel/',
        views.export_invoice_excel,
        name='export_invoice_excel'
    ),

    path(
    'invoice/<int:invoice_id>/',
    views.invoice_detail,
    name='invoice_detail'
    ),

    path(
    'invoice/<int:invoice_id>/paid/',
    views.mark_invoice_paid,
    name='mark_invoice_paid'
    ),

    path(
    'invoice/<int:invoice_id>/pdf/',
    views.invoice_pdf,
    name='invoice_pdf'
    ),

    path(
    'my-invoices/',
    views.my_invoices,
    name='my_invoices'
    ),

    path(
    'invoice/<int:invoice_id>/',
    views.invoice_detail,
    name='invoice_detail'
    ),

    path(
    'invoice/<int:invoice_id>/add-item/',
    views.add_invoice_item,
    name='add_invoice_item'
    ),

]