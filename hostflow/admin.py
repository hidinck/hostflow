from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Property, Unit, Lease, Payment,
    MaintenanceTicket, TicketComment, Notification, AuditLog
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('username', 'email', 'role', 'phone', 'is_active')
    list_filter   = ('role',)
    fieldsets     = BaseUserAdmin.fieldsets + (
        ('HostFlow', {'fields': ('role', 'phone')}),
    )


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'owner')
    list_filter  = ('city',)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'property', 'rent_amount', 'status')
    list_filter  = ('status', 'rent_type')


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'unit', 'start_date', 'end_date', 'status')
    list_filter  = ('status',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('lease', 'amount_due', 'amount_paid', 'due_date', 'status')
    list_filter  = ('status',)


@admin.register(MaintenanceTicket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit', 'priority', 'status', 'created_at')
    list_filter  = ('status', 'priority')


admin.site.register(TicketComment)
admin.site.register(Notification)
admin.site.register(AuditLog)
