from allauth.account.forms import SignupForm
from django import forms
from .models import Property, Tenant, Payment, MaintenanceRequest, Profile

class CustomSignupForm(SignupForm):
    ROLE_CHOICES = (
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    def save(self, request):
        user = super().save(request)

        
        profile, created = Profile.objects.get_or_create(user=user)
        profile.role = self.cleaned_data['role']
        profile.save()

        return user


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['image','name', 'address', 'rent_amount', 'is_occupied']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['issue_type', 'description', 'urgency']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method', 'transaction_code']