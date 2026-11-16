from django.contrib import admin
from .models import Sale


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'property',
        'customer',
        'agent',
        'selling_price',
        'sale_date',
        'payment_status',
    )

    list_filter = ('payment_status', 'sale_date')
    search_fields = (
        'property__title',
        'customer__name',
        'customer__phone',
    )