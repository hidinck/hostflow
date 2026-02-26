"""
HostFlow Utilities
==================
Email notifications + Audit log helper.
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


# ── Email helpers ──────────────────────────────────────────────────────────────

def send_notification_email(recipient_email, subject, message):
    """Send a plain-text email. Fails silently so app never crashes on email error."""
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [recipient_email],
            fail_silently=True,
        )
        return True
    except Exception:
        return False


def notify_rent_due(payment):
    tenant = payment.lease.tenant
    subject = f"[HostFlow] Rent Due – ₹{payment.amount_due}"
    message = (
        f"Hi {tenant.get_full_name() or tenant.username},\n\n"
        f"Your rent of ₹{payment.amount_due} is due on {payment.due_date}.\n"
        f"Please pay on time to avoid late fees.\n\n"
        f"– HostFlow"
    )
    send_notification_email(tenant.email, subject, message)


def notify_late_payment(payment):
    tenant = payment.lease.tenant
    subject = f"[HostFlow] Late Payment Alert – ₹{payment.late_fee} fee added"
    message = (
        f"Hi {tenant.get_full_name() or tenant.username},\n\n"
        f"Your rent payment of ₹{payment.amount_due} was due on {payment.due_date}.\n"
        f"A late fee of ₹{payment.late_fee} has been added.\n"
        f"Please clear dues immediately.\n\n"
        f"– HostFlow"
    )
    send_notification_email(tenant.email, subject, message)


def notify_maintenance_update(ticket):
    user = ticket.submitted_by
    subject = f"[HostFlow] Maintenance Update – {ticket.title}"
    message = (
        f"Hi {user.get_full_name() or user.username},\n\n"
        f"Your maintenance ticket '{ticket.title}' status is now: {ticket.get_status_display()}.\n\n"
        f"– HostFlow"
    )
    send_notification_email(user.email, subject, message)


def notify_lease_expiry(lease):
    tenant = lease.tenant
    subject = f"[HostFlow] Lease Expiring Soon – {lease.unit}"
    message = (
        f"Hi {tenant.get_full_name() or tenant.username},\n\n"
        f"Your lease for {lease.unit} expires on {lease.end_date}.\n"
        f"Please contact your landlord for renewal.\n\n"
        f"– HostFlow"
    )
    send_notification_email(tenant.email, subject, message)


# ── Audit Log helper ───────────────────────────────────────────────────────────

def log_action(user, action, model_name, object_id, description):
    """Create an AuditLog entry. Import here to avoid circular imports."""
    from .models import AuditLog
    AuditLog.objects.create(
        performed_by=user,
        action=action,
        model_name=model_name,
        object_id=object_id,
        description=description,
    )
