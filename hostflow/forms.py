from django import forms
from .models import User, Property, Unit, Lease, Payment, MaintenanceTicket, TicketComment

# ── 1. AUTH FORMS ──────────────────────────────────────────────────────────

class LandlordRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control'})}

class TenantRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control'})}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role, user.is_active, user.is_verified = 'tenant', True, True
        user.set_password(self.cleaned_data['password'])
        if commit: user.save()
        return user

# ── 2. MANAGEMENT FORMS (WITH CALENDARS) ────────────────────────────────────

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['name', 'address', 'city']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['unit_number', 'rent_type', 'rent_amount', 'status']
        widgets = {
            'unit_number': forms.TextInput(attrs={'class': 'form-control'}),
            'rent_type': forms.Select(attrs={'class': 'form-select'}),
            'rent_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class LeaseForm(forms.ModelForm):
    class Meta:
        model = Lease
        fields = ['tenant', 'start_date', 'end_date', 'document']
        widgets = {
            'tenant': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tenant'].queryset = User.objects.filter(role='tenant')

class ManualPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'paid_date', 'notes']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'paid_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

# ── 3. MAINTENANCE FORMS ─────────────────────────────────────────────────────

class MaintenanceTicketForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTicket
        fields = ['title', 'description', 'priority', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['content']
        widgets = {'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})}

class TicketStatusForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTicket
        fields = ['status']
        widgets = {'status': forms.Select(attrs={'class': 'form-select'})}