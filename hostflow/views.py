from django.core.mail import send_mail
from django.conf import settings
import json, random, csv
from datetime import date, timedelta
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import (
    User, Property, Unit, Lease, Payment,
    MaintenanceTicket, TicketComment, Notification, AuditLog
)
from .forms import *
from .utils import log_action

def update_lease_status():
    today = timezone.now().date()
    Lease.objects.filter(end_date__lt=today, status='active').update(status='expired')
def generate_rent():
    today = timezone.now().date()

    leases = Lease.objects.filter(status='active')

    for lease in leases:
        exists = Payment.objects.filter(
            lease=lease,
            due_date__month=today.month,
            due_date__year=today.year
        ).exists()

        if not exists:
            Payment.objects.create(
                lease=lease,
                amount_due=lease.unit.rent_amount,
                due_date=today.replace(day=5)
            )
# ── LANDING & AUTH ──────────────────────────────────────────────────────────

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('tenant_portal' if request.user.role == 'tenant' else 'dashboard')
    return render(request, 'hostflow/landing.html')

def landlord_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'landlord':
            messages.error(request, "Landlord access only.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

def tenant_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'tenant':
            messages.error(request, "Tenant access only.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import json, random


@csrf_exempt
def send_email_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('email')

            if not email:
                return JsonResponse({'status': 'fail', 'error': 'No email provided'})

            otp = str(random.randint(100000, 999999))

            # Save OTP in session
            request.session['email'] = email
            request.session['email_otp'] = otp
            request.session['email_verified'] = False

            try:
                send_mail(
                    'HostFlow OTP',
                    f'Your OTP is {otp}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                print("OTP sent:", otp)

            except Exception as e:
                print("EMAIL ERROR:", str(e))
                return JsonResponse({
                    'status': 'fail',
                    'error': str(e)
                })

            return JsonResponse({'status': 'success'})

        except Exception as e:
            print("GENERAL ERROR:", str(e))
            return JsonResponse({
                'status': 'fail',
                'error': str(e)
            })

@csrf_exempt
def verify_email_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        if data.get('otp') == request.session.get('email_otp'):
            request.session['email_verified'] = True
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})

def register_view(request):
    if request.method == 'POST':
        if not request.session.get('email_verified'):
            messages.error(request, "Verify email first.")
            return redirect('register')
        form = LandlordRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(request.POST.get('password'))
            user.role, user.is_verified, user.is_active = 'landlord', True, True
            user.save()
            return redirect('login')
    return render(request, 'hostflow/register.html', {'form': LandlordRegisterForm()})

def login_view(request):
    if request.method == 'POST':
        u, p = request.POST.get('username'), request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            if not getattr(user, 'is_verified', True):
                messages.error(request, "Account not verified.")
                return redirect('register')
            login(request, user)
            return redirect('tenant_portal' if user.role == 'tenant' else 'dashboard')
        messages.error(request, "Invalid username or password.")
    return render(request, 'hostflow/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('landing')

# ── LANDLORD DASHBOARD ───────────────────────────────────────────────────────

@login_required
@landlord_required
def dashboard(request):
    update_lease_status()
    generate_rent()
    props = Property.objects.filter(owner=request.user)
    units = Unit.objects.filter(property__in=props)
    leases = Lease.objects.filter(unit__in=units)
    payments = Payment.objects.filter(lease__unit__property__owner=request.user)

    today = timezone.now().date()

    monthly_income = payments.filter(
        status='paid',
        paid_date__year=today.year,
        paid_date__month=today.month
    ).aggregate(total=Sum('amount_paid'))['total'] or 0

    context = {
        'total_properties': props.count(),
        'total_units': units.count(),
        'occupied_units': units.filter(status='occupied').count(),
        'vacant_units': units.filter(status='vacant').count(),
        'active_tenants': leases.filter(status='active').count(),
        'monthly_income': monthly_income,
        'overdue_payments': payments.filter(due_date__lt=today, status__in=['pending', 'partial']).count(),
        'open_tickets': MaintenanceTicket.objects.filter(unit__in=units, status='open').count(),
        'recent_payments': payments.order_by('-created_at')[:5],
        'notifications': Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5],
        'total_overdue': payments.filter(status='overdue').count(),
        'expiring_soon': [l for l in leases if today <= l.end_date <= today + timedelta(days=30)],
        'expired_leases': [l for l in leases if l.end_date < today],
    }

    return render(request, 'hostflow/dashboard.html', context)

# ── PROPERTY & UNIT MANAGEMENT ───────────────────────────────────────────────

@login_required
@landlord_required
def property_list(request):
    return render(request, 'hostflow/property_list.html', {'properties': Property.objects.filter(owner=request.user)})

@login_required
@landlord_required
def property_add(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False); p.owner = request.user; p.save()
            return redirect('property_list')
    return render(request, 'hostflow/property_form.html', {'form': PropertyForm(), 'action': 'Add'})

@login_required
@landlord_required
def property_edit(request, pk):
    prop = get_object_or_404(Property, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=prop)
        if form.is_valid(): form.save(); return redirect('property_list')
    return render(request, 'hostflow/property_form.html', {'form': PropertyForm(instance=prop), 'action': 'Edit'})

@login_required
@landlord_required
def property_delete(request, pk):
    prop = get_object_or_404(Property, pk=pk, owner=request.user)
    if request.method == 'POST': prop.delete(); return redirect('property_list')
    return render(request, 'hostflow/confirm_delete.html', {'object': prop})

@login_required
@landlord_required
def unit_list(request, property_pk):
    prop = get_object_or_404(Property, pk=property_pk, owner=request.user)
    return render(request, 'hostflow/unit_list.html', {'property': prop, 'units': prop.units.all()})

@login_required
@landlord_required
def unit_add(request, property_pk):
    prop = get_object_or_404(Property, pk=property_pk, owner=request.user)
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            u = form.save(commit=False); u.property = prop; u.save()
            return redirect('unit_list', property_pk=prop.pk)
    return render(request, 'hostflow/unit_form.html', {'form': UnitForm(), 'property': prop, 'action': 'Add'})

@login_required
@landlord_required
def unit_edit(request, pk):
    unit = get_object_or_404(Unit, pk=pk, property__owner=request.user)
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid(): form.save(); return redirect('unit_list', property_pk=unit.property.pk)
    return render(request, 'hostflow/unit_form.html', {'form': UnitForm(instance=unit), 'property': unit.property, 'action': 'Edit'})

# ── LEASE MANAGEMENT ─────────────────────────────────────────────────────────

@login_required
@landlord_required
def lease_list(request):
    units = Unit.objects.filter(property__owner=request.user)
    leases = Lease.objects.filter(unit__in=units).select_related('tenant', 'unit')

    today = date.today()

    for lease in leases:
        if lease.end_date < today:
            lease.status_display = "Expired"
            lease.status_color = "danger"
        elif lease.end_date <= today + timedelta(days=30):
            lease.status_display = "Expiring Soon"
            lease.status_color = "warning"
        else:
            lease.status_display = "Active"
            lease.status_color = "success"

    return render(request, 'hostflow/lease_list.html', {'leases': leases})

@login_required
@landlord_required
def lease_add(request, unit_pk):
    unit = get_object_or_404(Unit, pk=unit_pk, property__owner=request.user)
    if request.method == 'POST':
        form = LeaseForm(request.POST, request.FILES)
        if form.is_valid():
            tenant = form.cleaned_data['tenant']
            Lease.objects.filter(unit=unit, tenant=tenant, status='terminated').delete()
            if Lease.objects.filter(unit=unit, tenant=tenant, status='active').exists():
                messages.error(request, "Active lease already exists.")
                return render(request, 'hostflow/lease_form.html', {'form': form, 'unit': unit})
            l = form.save(commit=False); l.unit = unit; l.save()
            unit.status = 'occupied'; unit.save()
            return redirect('lease_list')
    return render(request, 'hostflow/lease_form.html', {'form': LeaseForm(), 'unit': unit})

@login_required
@landlord_required
def lease_terminate(request, pk):
    lease = get_object_or_404(Lease, pk=pk, unit__property__owner=request.user)
    if request.method == 'POST':
        lease.status = 'terminated'; lease.save()
        lease.unit.status = 'vacant'; lease.unit.save()
        return redirect('lease_list')
    return render(request, 'hostflow/confirm_delete.html', {'object': lease, 'action_label': 'Terminate'})

# ── PAYMENTS & LATE FEES ─────────────────────────────────────────────────────

@login_required
@landlord_required
def payment_list(request):
    units = Unit.objects.filter(property__owner=request.user)
    payments = Payment.objects.filter(lease__unit__in=units).order_by('-due_date')

    today = timezone.now().date()

    for p in payments:
        p.late_fee = p.calculate_late_fee()

        if p.status != 'paid' and p.due_date < today:
            p.status = 'overdue'

    return render(request, 'hostflow/payment_list.html', {'payments': payments})

@login_required
@landlord_required
def payment_add(request, lease_pk):
    lease = get_object_or_404(Lease, pk=lease_pk, unit__property__owner=request.user)
    if request.method == 'POST':
        form = ManualPaymentForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False); p.lease = lease
            p.amount_due = lease.unit.rent_amount; p.due_date = date.today(); p.save()
            return redirect('payment_list')
    return render(request, 'hostflow/payment_form.html', {'form': ManualPaymentForm(), 'lease': lease})

@login_required
@landlord_required
def reports(request):
    payments = Payment.objects.filter(lease__unit__property__owner=request.user)

    monthly_data = []

    for i in range(5, -1, -1):
        start = date.today().replace(day=1) - relativedelta(months=i)
        end = start + relativedelta(months=1)

        total = payments.filter(
            status='paid',
            paid_date__gte=start,
            paid_date__lt=end
        ).aggregate(t=Sum('amount_paid'))['t'] or 0

        monthly_data.append({
            'month': start.strftime('%b %Y'),
            'total': float(total)
        })

    prop_revenue = []
    for prop in Property.objects.filter(owner=request.user):
        rev = Payment.objects.filter(
            lease__unit__property=prop,
            status='paid'
        ).aggregate(t=Sum('amount_paid'))['t'] or 0

        prop_revenue.append({'name': prop.name, 'revenue': float(rev)})

    context = {
        'monthly_data': json.dumps(monthly_data),
        'prop_revenue': json.dumps(prop_revenue),
        'total_collected': payments.filter(status='paid').aggregate(t=Sum('amount_paid'))['t'] or 0,
        'occupancy_rate': round(
            Unit.objects.filter(property__owner=request.user, status='occupied').count()
            / max(Unit.objects.filter(property__owner=request.user).count(), 1) * 100, 1
        ),
    }

    return render(request, 'hostflow/reports.html', context)

@login_required
@landlord_required
def export_payments_csv(request):
    payments = Payment.objects.filter(lease__unit__property__owner=request.user).order_by('-due_date')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'
    writer = csv.writer(response)
    writer.writerow(['Tenant', 'Unit', 'Amount Due', 'Paid', 'Status'])
    for p in payments:
        writer.writerow([p.lease.tenant.username, p.lease.unit.unit_number, p.amount_due, p.amount_paid, p.status])
    return response

# ── AUDIT, TICKETS & NOTIFICATIONS ───────────────────────────────────────────

@login_required
@landlord_required
def audit_log_list(request):
    # 🔥 FIXED: Logic to show history correctly
    logs = AuditLog.objects.filter(performed_by=request.user).order_by('-created_at')
    return render(request, 'hostflow/audit_logs.html', {'logs': logs})

@login_required
def notification_list(request):
    notifs = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'hostflow/notification_list.html', {'notifications': notifs})

@login_required
def ticket_list(request):
    units = Unit.objects.filter(property__owner=request.user)
    return render(request, 'hostflow/ticket_list.html', {'tickets': MaintenanceTicket.objects.filter(unit__in=units)})

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(MaintenanceTicket, pk=pk)
    if request.method == 'POST':
        if 'add_comment' in request.POST:
            form = TicketCommentForm(request.POST)
            if form.is_valid():
                c = form.save(commit=False); c.ticket = ticket; c.author = request.user; c.save()
        elif 'update_status' in request.POST:
            form = TicketStatusForm(request.POST, instance=ticket)
            if form.is_valid(): form.save()
        return redirect('ticket_detail', pk=pk)
    return render(request, 'hostflow/ticket_detail.html', {'ticket': ticket, 'comment_form': TicketCommentForm(), 'status_form': TicketStatusForm(instance=ticket)})

# ── TENANT PORTAL ────────────────────────────────────────────────────────────

@login_required
@tenant_required
def tenant_portal(request):
    leases = Lease.objects.filter(tenant=request.user, status='active')
    payments = Payment.objects.filter(lease__in=leases).order_by('-due_date')

    for p in payments:
        p.late_fee = p.calculate_late_fee()

    tickets = MaintenanceTicket.objects.filter(submitted_by=request.user).order_by('-created_at')

    return render(request, 'hostflow/tenant_portal.html', {
        'leases': leases,
        'payments': payments,
        'tickets': tickets
    })
@login_required
@tenant_required
def tenant_submit_ticket(request):
    lease = Lease.objects.filter(tenant=request.user, status='active').first()
    if request.method == 'POST':
        form = MaintenanceTicketForm(request.POST, request.FILES)
        if form.is_valid():
            t = form.save(commit=False); t.unit = lease.unit; t.submitted_by = request.user; t.save()
            return redirect('tenant_portal')
    return render(request, 'hostflow/ticket_form.html', {'form': MaintenanceTicketForm()})

@login_required
def download_receipt(request, payment_pk):
    payment = get_object_or_404(Payment, pk=payment_pk)
    if request.user.role == 'tenant' and payment.lease.tenant != request.user:
        return HttpResponse("Forbidden", status=403)
    
    # 🔥 Restored Professional Detailed Receipt Layout
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment_pk}.txt"'
    
    late_fee = payment.calculate_late_fee()
    total_due = payment.amount_due + late_fee
    
    response.write(f"""
==========================================
        HOSTFLOW PAYMENT RECEIPT
==========================================
Receipt ID  : HF-{payment.pk}
Tenant      : {payment.lease.tenant.username}
Property    : {payment.lease.unit.property.name}
Unit        : {payment.lease.unit.unit_number}
------------------------------------------
Base Rent   : ₹{payment.amount_due}
Late Fees   : ₹{late_fee}
Total Due   : ₹{payment.amount_due + late_fee}
------------------------------------------
Paid Amount : ₹{payment.amount_paid}
Paid Date   : {payment.paid_date or 'N/A'}
Status      : {payment.get_status_display()}
==========================================
    """)
    return response

@login_required
@landlord_required
def add_tenant(request):
    if request.method == 'POST':
        form = TenantRegisterForm(request.POST)
        if form.is_valid():
            form.save(); messages.success(request, "Tenant created."); return redirect('lease_list')
        else:
            for field, errors in form.errors.items():
                for error in errors: messages.error(request, f"{field}: {error}")
    return render(request, 'hostflow/add_tenant.html', {'form': TenantRegisterForm()})
@login_required
@tenant_required
def pay_rent(request, payment_pk):
    payment = get_object_or_404(Payment, pk=payment_pk, lease__tenant=request.user)

    if payment.status == 'paid':
        messages.warning(request, "Already paid.")
        return redirect('tenant_portal')

    today = timezone.now().date()

    # Calculate late fee
    late_fee = payment.calculate_late_fee()
    total_due = payment.amount_due + late_fee

    if request.method == 'POST':
        payment.amount_paid = total_due
        payment.late_fee = late_fee
        payment.paid_date = today
        payment.status = 'paid'
        payment.save()

        messages.success(request, "Payment successful!")
        return redirect('tenant_portal')

    return render(request, 'hostflow/pay_rent.html', {
        'payment': payment,
        'late_fee': late_fee,
        'total_due': total_due
    })