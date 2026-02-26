"""
HostFlow Unit Tests
===================
Covers: Auth, Tenant isolation, Payment logic, Late fee, API endpoints.
Run with: python manage.py test hostflow
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import User, Property, Unit, Lease, Payment, MaintenanceTicket


def make_landlord(username='landlord1', password='testpass123'):
    return User.objects.create_user(
        username=username, password=password, role='landlord', email=f'{username}@test.com'
    )

def make_tenant(username='tenant1', password='testpass123'):
    return User.objects.create_user(
        username=username, password=password, role='tenant', email=f'{username}@test.com'
    )

def make_property(owner):
    return Property.objects.create(
        owner=owner, name='Test Property', address='123 Main St', city='Delhi'
    )

def make_unit(prop, number='A1', rent=5000):
    return Unit.objects.create(
        property=prop, unit_number=number,
        rent_type='monthly', rent_amount=rent, status='vacant'
    )

def make_lease(unit, tenant):
    return Lease.objects.create(
        unit=unit, tenant=tenant,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        status='active'
    )


# ── Auth Tests ─────────────────────────────────────────────────────────────────

class AuthTests(TestCase):
    def test_landlord_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newlandlord',
            'email': 'newlandlord@test.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(User.objects.filter(username='newlandlord').count(), 1)
        user = User.objects.get(username='newlandlord')
        self.assertEqual(user.role, 'landlord')

    def test_login_valid(self):
        make_landlord('ll_login', 'pass12345!')
        response = self.client.post(reverse('login'), {
            'username': 'll_login', 'password': 'pass12345!'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': 'nobody', 'password': 'wrongpass'
        })
        # Should stay on login page (no redirect)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # redirects to login


# ── Tenant Isolation Tests ──────────────────────────────────────────────────────

class TenantIsolationTests(TestCase):
    def setUp(self):
        self.landlord1 = make_landlord('ll1')
        self.landlord2 = make_landlord('ll2')
        self.prop1 = make_property(self.landlord1)
        self.prop2 = make_property(self.landlord2)

    def test_landlord_sees_only_own_properties(self):
        self.client.force_login(self.landlord1)
        response = self.client.get(reverse('property_list'))
        # landlord1 sees prop1 only
        self.assertContains(response, self.prop1.name)
        self.assertNotContains(response, self.prop2.name)

    def test_landlord_cannot_delete_others_property(self):
        self.client.force_login(self.landlord1)
        response = self.client.post(
            reverse('property_delete', args=[self.prop2.pk])
        )
        # Should 404 because get_object_or_404 includes owner=request.user
        self.assertEqual(response.status_code, 404)


# ── Payment & Late Fee Tests ───────────────────────────────────────────────────

class PaymentTests(TestCase):
    def setUp(self):
        self.landlord = make_landlord()
        self.tenant   = make_tenant()
        self.prop     = make_property(self.landlord)
        self.unit     = make_unit(self.prop)
        self.lease    = make_lease(self.unit, self.tenant)

    def test_payment_status_paid(self):
        p = Payment.objects.create(
            lease=self.lease,
            amount_due=Decimal('5000'),
            amount_paid=Decimal('5000'),
            due_date=date.today(),
        )
        self.assertEqual(p.status, 'paid')

    def test_payment_status_partial(self):
        p = Payment.objects.create(
            lease=self.lease,
            amount_due=Decimal('5000'),
            amount_paid=Decimal('2000'),
            due_date=date.today(),
        )
        self.assertEqual(p.status, 'partial')

    def test_payment_status_overdue(self):
        p = Payment.objects.create(
            lease=self.lease,
            amount_due=Decimal('5000'),
            amount_paid=Decimal('0'),
            due_date=date.today() - timedelta(days=35),
        )
        self.assertEqual(p.status, 'overdue')

    def test_late_fee_calculated(self):
        p = Payment.objects.create(
            lease=self.lease,
            amount_due=Decimal('5000'),
            amount_paid=Decimal('0'),
            due_date=date.today() - timedelta(days=35),
        )
        self.assertGreater(p.late_fee, 0)

    def test_rent_amount_non_negative(self):
        from django.core.exceptions import ValidationError
        unit = Unit(
            property=self.prop, unit_number='Z9',
            rent_type='monthly', rent_amount=-100, status='vacant'
        )
        with self.assertRaises(Exception):
            unit.full_clean()


# ── Maintenance Tests ──────────────────────────────────────────────────────────

class MaintenanceTests(TestCase):
    def setUp(self):
        self.landlord = make_landlord()
        self.tenant   = make_tenant()
        self.prop     = make_property(self.landlord)
        self.unit     = make_unit(self.prop)
        self.lease    = make_lease(self.unit, self.tenant)

    def test_tenant_can_submit_ticket(self):
        self.client.force_login(self.tenant)
        response = self.client.post(reverse('submit_ticket'), {
            'title': 'Leaking pipe',
            'description': 'Kitchen pipe is leaking.',
            'priority': 'high',
        })
        self.assertEqual(MaintenanceTicket.objects.filter(title='Leaking pipe').count(), 1)

    def test_ticket_default_status_is_open(self):
        ticket = MaintenanceTicket.objects.create(
            unit=self.unit,
            submitted_by=self.tenant,
            title='Test', description='Test', priority='low'
        )
        self.assertEqual(ticket.status, 'open')


# ── DB Constraint Tests ────────────────────────────────────────────────────────

class DBConstraintTests(TestCase):
    def setUp(self):
        self.landlord = make_landlord()
        self.prop     = make_property(self.landlord)

    def test_unique_unit_number_per_property(self):
        from django.db import IntegrityError
        make_unit(self.prop, 'A1')
        with self.assertRaises(IntegrityError):
            make_unit(self.prop, 'A1')  # duplicate

    def test_same_unit_number_different_property(self):
        prop2 = make_property(self.landlord)
        make_unit(self.prop, 'A1')
        unit2 = make_unit(prop2, 'A1')   # should succeed
        self.assertIsNotNone(unit2.pk)
