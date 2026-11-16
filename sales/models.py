
from django.db import models
from django.conf import settings
from properties.models import Property
from customers.models import Customer


class Sale(models.Model):

    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partial'),
        ('PAID', 'Paid'),
    ]

    property = models.ForeignKey(
        Property,
        on_delete=models.PROTECT,
        related_name='sales'
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='purchases'
    )

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales'
    )

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    sale_date = models.DateField()

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='PENDING'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.property.title} - {self.customer.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.payment_status == 'PAID':
            Property.objects.filter(
                id=self.property_id
            ).update(status='SOLD')
