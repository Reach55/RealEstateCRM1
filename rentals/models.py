from django.db import models
from django.conf import settings
from properties.models import Property
from customers.models import Customer


class Rental(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('ACTIVE', 'Active'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')]
    tenant = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='rentals')
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='rentals')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rentals')
    monthly_rent = models.DecimalField(max_digits=12, decimal_places=2)
    deposit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status in ('CONFIRMED', 'ACTIVE'):
            Property.objects.filter(pk=self.property_id).update(status='RENTED')

    def __str__(self):
        return f'{self.property.title} - {self.tenant.name}'
