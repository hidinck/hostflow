from django.urls import path
from . import views

urlpatterns = [
    # ── LANDING & OTP ──────────────────────────────────────────
    path('', views.landing_page, name='landing'),
    path('send-email-otp/', views.send_email_otp, name='send_email_otp'),
    path('verify-email-otp/', views.verify_email_otp, name='verify_email_otp'),

    # ── AUTH ───────────────────────────────────────────────────
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # ── DASHBOARD ──────────────────────────────────────────────
    path('dashboard/', views.dashboard, name='dashboard'),

    # ── PROPERTIES ─────────────────────────────────────────────
    path('properties/', views.property_list, name='property_list'),
    path('properties/add/', views.property_add, name='property_add'),
    path('properties/<int:pk>/edit/', views.property_edit, name='property_edit'),
    path('properties/<int:pk>/delete/', views.property_delete, name='property_delete'),

    # ── UNITS ──────────────────────────────────────────────────
    path('properties/<int:property_pk>/units/', views.unit_list, name='unit_list'),
    path('properties/<int:property_pk>/units/add/', views.unit_add, name='unit_add'),
    path('units/<int:pk>/edit/', views.unit_edit, name='unit_edit'),

    # ── LEASES ─────────────────────────────────────────────────
    path('leases/', views.lease_list, name='lease_list'),
    path('leases/add/<int:unit_pk>/', views.lease_add, name='lease_add'),
    path('leases/<int:pk>/terminate/', views.lease_terminate, name='lease_terminate'),

    # ── TENANTS ────────────────────────────────────────────────
    path('tenants/add/', views.add_tenant, name='add_tenant'),

    # ── PAYMENTS ───────────────────────────────────────────────
    path('pay/<int:payment_pk>/', views.pay_rent, name='pay_rent'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/add/<int:lease_pk>/', views.payment_add, name='payment_add'),
    path('payments/<int:payment_pk>/receipt/', views.download_receipt, name='download_receipt'),

    # ── MAINTENANCE ────────────────────────────────────────────
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),

    # ── NOTIFICATIONS ──────────────────────────────────────────
    path('notifications/', views.notification_list, name='notification_list'),

    # ── REPORTS ────────────────────────────────────────────────
    path('reports/', views.reports, name='reports'),
    path('reports/export/csv/', views.export_payments_csv, name='export_csv'),

    # ── AUDIT ──────────────────────────────────────────────────
    path('audit/', views.audit_log_list, name='audit_logs'),

    # ── TENANT PORTAL ──────────────────────────────────────────
    path('tenant/', views.tenant_portal, name='tenant_portal'),
    path('tenant/maintenance/submit/', views.tenant_submit_ticket, name='submit_ticket'),
]