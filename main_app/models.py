from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=(('tenant', 'Tenant'), ('landlord', 'Landlord')))
    # Add more fields as needed

    def __str__(self):
        return f"{self.user.username}'s profile"


class Property(models.Model):
    image = models.ImageField(upload_to='property_images/', blank=True, null=True)
    name = models.CharField(max_length=100)
    address = models.TextField()
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.address}"

class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    id_number = models.CharField(max_length=20)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.get_full_name()

class Payment(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    method = models.CharField(max_length=50)
    transaction_code = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.tenant.user.username} - {self.amount} on {self.payment_date}"
    
class MaintenanceRequest(models.Model):
    URGENCY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    )

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    issue_type = models.CharField(max_length=100)  # e.g., Plumbing, Electrical
    description = models.TextField()
    urgency = models.CharField(max_length=10, choices=URGENCY_LEVELS)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.issue_type} - {self.status}"