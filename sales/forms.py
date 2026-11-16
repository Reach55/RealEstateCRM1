from django import forms
import re

from .models import Sale
from properties.models import Property


class SaleForm(forms.ModelForm):
    property = forms.CharField(
        label='House ID',
        help_text='Search or enter the generated House ID, for example LGS-000001.',
        widget=forms.TextInput(attrs={
            'list': 'house-id-options',
            'placeholder': 'Search by House ID',
            'autocomplete': 'off',
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available = Property.objects.filter(
            listing_type='SALE',
            status='AVAILABLE',
        )
        if self.instance.pk and self.instance.property_id:
            available = available | Property.objects.filter(pk=self.instance.property_id)
            self.initial['property'] = self.instance.property.house_id
        self.available_properties = available.select_related('agent').order_by('pk').distinct()

    def clean_property(self):
        value = self.cleaned_data['property'].strip().upper()
        match = re.fullmatch(r'LGS-(\d+)', value)
        if not match:
            raise forms.ValidationError('Enter a House ID in the format LGS-000001.')

        property_obj = Property.objects.filter(pk=int(match.group(1))).first()
        if property_obj is None or not self.available_properties.filter(pk=property_obj.pk).exists():
            raise forms.ValidationError('No available sale property matches that House ID.')
        return property_obj

    class Meta:
        model = Sale
        fields = [
            'property',
            'customer',
            'agent',
            'selling_price',
            'sale_date',
            'payment_status',
            'notes',
        ]

        widgets = {
            'sale_date': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'notes': forms.Textarea(
                attrs={'rows': 3}
            ),
        }
