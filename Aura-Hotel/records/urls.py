from django.urls import path
from . import views

urlpatterns = [

    path(
        'audit-dashboard/',
        views.audit_dashboard,
        name='audit_dashboard'
    ),

    path(
    'audit/export/pdf/',
    views.export_audit_pdf,
    name='export_audit_pdf'
    ),

    path(
    'audit/export/excel/',
    views.export_audit_excel,
    name='export_audit_excel'
    ),

]