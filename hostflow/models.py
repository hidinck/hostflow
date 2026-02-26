"""
HostFlow Models (Clean Version)
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.utils import timezone
import random


# ══════════════════════════════════════════════════════════════════════════════
# 1. CUSTOM USER
# ══════════════════════════════════════════════════════════════════════════════

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='landlord')
    phone = models.CharField(max_length=15, blank=True)

    # OTP fields
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()

    def is_landlord(self):
        return self.role == 'landlord'

    def is_tenant(self):
        return self.role == 'tenant'

    def __str__(self):
        return f"{self.username} ({self.role})"


# ══════════════════════════════════════════════════════════════════════════════
# 2. PROPERTY & UNIT
# ══════════════════════════════════════════════════════════════════════════════

class Property(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'landlord'},
        related_name='properties'
    )
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Properties'

    def __str__(self):
        return f"{self.name} – {self.city}"

    def occupancy_rate(self):
        total = self.units.count()
        if total == 0:
            return 0
        occupied = self.units.filter(status='occupied').count()
        return round((occupied / total) * 100, 1)


class Unit(models.Model):
    RENT_TYPE_CHOICES = [
        ('monthly', 'Monthly'),
        ('daily', 'Daily')
    ]

    STATUS_CHOICES = [
        ('vacant', 'Vacant'),
        ('occupied', 'Occupied')
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='units')
    unit_number = models.CharField(max_length=20)
    rent_type = models.CharField(max_length=10, choices=RENT_TYPE_CHOICES, default='monthly')
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='vacant')

    class Meta:
        unique_together = ('property', 'unit_number')

    def __str__(self):
        return f"Unit {self.unit_number} – {self.property.name}"


# ══════════════════════════════════════════════════════════════════════════════
# 3. LEASE
# ══════════════════════════════════════════════════════════════════════════════

class Lease(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated')
    ]

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='leases')
    tenant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'tenant'},
        related_name='leases'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    document = models.FileField(upload_to='leases/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['unit', 'tenant'],
                condition=models.Q(status='active'),
                name='unique_active_lease_per_unit_tenant'
            )
        ]

    def __str__(self):
        return f"{self.tenant.username} @ {self.unit}"

    def is_expiring_soon(self):
        return (self.end_date - timezone.now().date()).days <= 30


# ══════════════════════════════════════════════════════════════════════════════
# 4. PAYMENT
# ══════════════════════════════════════════════════════════════════════════════

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('partial', 'Partial'),
    ]

    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payments')
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    late_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    notes = models.TextField(blank=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    receipt_number = models.CharField(max_length=50, blank=True, unique=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"₹{self.amount_due} – {self.lease.tenant.username} ({self.status})"

    def calculate_late_fee(self):
        today = timezone.now().date()

        if self.status != 'paid' and self.due_date < today:
            days_late = (today - self.due_date).days
            return days_late * 50

        return 0

    def save(self, *args, **kwargs):
        today = timezone.now().date()

        if self.due_date < today and self.status != 'paid':
            self.late_fee = self.calculate_late_fee()

        total_due = self.amount_due + self.late_fee

        if self.amount_paid >= total_due:
            self.status = 'paid'
            if not self.paid_date:
                self.paid_date = today
        elif self.amount_paid > 0:
            self.status = 'partial'
        elif today > self.due_date:
            self.status = 'overdue'
        else:
            self.status = 'pending'

        super().save(*args, **kwargs)

# ══════════════════════════════════════════════════════════════════════════════
# 5. MAINTENANCE
# ══════════════════════════════════════════════════════════════════════════════

class MaintenanceTicket(models.Model):
    PRIORITY_CHOICES = [('low','Low'), ('medium','Medium'), ('high','High')]
    STATUS_CHOICES = [('open','Open'), ('in_progress','In Progress'), ('resolved','Resolved')]

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='tickets')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    image = models.ImageField(upload_to='tickets/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.status})"


class TicketComment(models.Model):
    ticket = models.ForeignKey(MaintenanceTicket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# ══════════════════════════════════════════════════════════════════════════════
# 6. NOTIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


# ══════════════════════════════════════════════════════════════════════════════
# 7. AUDIT LOG
# ══════════════════════════════════════════════════════════════════════════════

class AuditLog(models.Model):
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)