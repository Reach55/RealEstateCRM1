
from django.db import models


class Property(models.Model):

    LISTING_TYPES = [
        ('SALE', 'For Sale'),
        ('RENT', 'For Rent'),
    ]

    PROPERTY_TYPES = [
        ('HOUSE', 'House'),
        ('VILLA', 'Villa'),
        ('TWIN_VILLA', 'Twin Villa'),
        ('LINK_HOUSE', 'Link House'),
        ('CONDO', 'Condo'),
        ('LAND', 'Land'),
        ('SHOPHOUSE', 'Shophouse'),
        ('APARTMENT', 'Apartment'),
        ('COMMERCIAL', 'Commercial Property'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('SOLD', 'Sold'),
        ('RENTED', 'Rented'),
        ('PENDING', 'Pending'),
        ('RESERVED', 'Reserved'),
    ]

    title = models.CharField(max_length=200)

    listing_type = models.CharField(
        max_length=10,
        choices=LISTING_TYPES,
        default='SALE'
    )

    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPES
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    monthly_rent = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    location = models.CharField(max_length=255)
    city = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    commune = models.CharField(max_length=100, blank=True)

    bedrooms = models.PositiveIntegerField(default=0)

    bathrooms = models.PositiveIntegerField(default=0)

    area = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    land_size = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    house_size = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    owner = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_properties')
    agent = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')

    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to='properties/',
        blank=True,
        null=True
    )

    features = models.TextField(
        blank=True,
        help_text="Swimming pool, garden, parking, elevator"
    )

    swimming_pool = models.BooleanField(default=False)

    parking = models.BooleanField(default=False)

    garden = models.BooleanField(default=False)

    furnished = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AVAILABLE'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def house_id(self):
        """Stable, human-readable ID derived from the database primary key."""
        return f'LGS-{self.pk:06d}' if self.pk else ''

    def __str__(self):
        return self.title


class PropertyPhoto(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='properties/')
    caption = models.CharField(max_length=200, blank=True)
