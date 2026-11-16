
from django.db import models
from django.conf import settings


class Customer(models.Model):

    CUSTOMER_TYPES = [
        ('BUYER', 'Buyer'),
        ('SELLER', 'Seller'),
        ('RENTER', 'Renter'),
        ('RENT_OWNER', 'Property Rent Owner'),
    ]
    PRICE_NEGOTIABILITY_CHOICES = [
        ('NEGOTIABLE', 'Negotiable'),
        ('FIXED', 'Not negotiable'),
    ]
    TITLE_TYPE_CHOICES = [
        ('HARD', 'Hard Title'),
        ('SOFT', 'Soft Title'),
    ]

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True, null=True)

    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPES,
        default='BUYER'
    )

    minimum_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    preferred_location = models.CharField(
        max_length=255,
        blank=True
    )

    preferred_bedrooms = models.PositiveIntegerField(default=0)
    preferred_bathrooms = models.PositiveIntegerField(default=0)

    requirements = models.TextField(
        blank=True,
        help_text="Example: Swimming pool, parking, garden"
    )

    notes = models.TextField(blank=True)

    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='customers'
    )
    property_type = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    commune = models.CharField(max_length=100, blank=True)
    preferred_city = models.CharField(max_length=100, blank=True)
    preferred_district = models.CharField(max_length=100, blank=True)
    preferred_commune = models.CharField(max_length=100, blank=True)
    owner_property_title = models.CharField(max_length=200, blank=True)
    asking_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_negotiability = models.CharField(max_length=12, choices=PRICE_NEGOTIABILITY_CHOICES, blank=True)
    title_type = models.CharField(max_length=10, choices=TITLE_TYPE_CHOICES, blank=True)
    owner_bedrooms = models.CharField(max_length=10, blank=True)
    owner_bathrooms = models.CharField(max_length=10, blank=True)
    land_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    house_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    furnished_status = models.CharField(max_length=20, blank=True)
    property_description = models.TextField(blank=True)
    owner_requirements = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
