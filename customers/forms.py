from django import forms
from decimal import Decimal
from accounts.models import User
from properties.models import Property
from properties.forms import PHNOM_PENH_DISTRICTS
from .models import Customer

PROPERTY_TYPES = Property.PROPERTY_TYPES
BEDROOM_CHOICES = [('0', 'Any / Studio'), *[(str(n), str(n)) for n in range(1, 6)], ('6', '6+')]
BATHROOM_CHOICES = [('0', 'Any'), *[(str(n), str(n)) for n in range(1, 5)], ('5', '5+')]
REQUIREMENT_CHOICES = [(x, x) for x in ('Swimming Pool', 'Parking', 'Garden', 'Fully Furnished', 'Semi Furnished', 'Gym', 'Elevator', 'Security', 'Near Main Road', 'Balcony', 'Air Conditioning', 'Pet Friendly', 'Other')]
CAMBODIAN_LOCATIONS = ['Phnom Penh', 'Banteay Meanchey', 'Battambang', 'Kampong Cham', 'Kampong Chhnang', 'Kampong Speu', 'Kampong Thom', 'Kampot', 'Kandal', 'Kep', 'Koh Kong', 'Kratie', 'Mondulkiri', 'Oddar Meanchey', 'Pailin', 'Preah Sihanouk', 'Preah Vihear', 'Prey Veng', 'Pursat', 'Ratanakiri', 'Siem Reap', 'Stung Treng', 'Svay Rieng', 'Takeo', 'Tbong Khmum']


class CustomerForm(forms.ModelForm):
    property_type = forms.ChoiceField(choices=[('', 'Select property type'), *PROPERTY_TYPES], required=False)
    city = forms.ChoiceField(choices=[('', 'Select city / province'), *[(name, name) for name in CAMBODIAN_LOCATIONS]], required=False)
    preferred_city = forms.ChoiceField(choices=[('', 'Select city / province'), *[(name, name) for name in CAMBODIAN_LOCATIONS]], required=False)
    district = forms.ChoiceField(choices=[('', 'Select Phnom Penh district'), *PHNOM_PENH_DISTRICTS], required=False)
    preferred_location = forms.ChoiceField(label='Preferred district', choices=[('', 'Select Phnom Penh district'), *PHNOM_PENH_DISTRICTS], required=False)
    minimum_budget = forms.DecimalField(label='Minimum budget ($)', max_digits=12, decimal_places=2, min_value=0, required=False, widget=forms.NumberInput(attrs={'min': '0', 'step': '0.01', 'placeholder': 'Minimum budget'}))
    budget = forms.DecimalField(label='Maximum budget ($)', max_digits=12, decimal_places=2, min_value=0, required=False, widget=forms.NumberInput(attrs={'min': '0', 'step': '0.01', 'placeholder': 'Maximum budget'}))
    price_negotiability = forms.ChoiceField(label='Price negotiable?', choices=[('', 'Select price terms'), *Customer.PRICE_NEGOTIABILITY_CHOICES], required=False)
    title_type = forms.ChoiceField(label='Title type', choices=[('', 'Select title type'), *Customer.TITLE_TYPE_CHOICES], required=False)
    furnished_status = forms.ChoiceField(choices=[('', 'Select furnishing'), ('FULL', 'Fully Furnished'), ('SEMI', 'Semi Furnished'), ('NONE', 'Unfurnished')], required=False)
    requirements = forms.MultipleChoiceField(choices=REQUIREMENT_CHOICES, required=False, widget=forms.SelectMultiple(attrs={'size': 6, 'class': 'requirements-source'}))
    preferred_bedrooms = forms.TypedChoiceField(choices=BEDROOM_CHOICES, coerce=int, required=False, empty_value=0)
    preferred_bathrooms = forms.TypedChoiceField(choices=BATHROOM_CHOICES, coerce=int, required=False, empty_value=0)
    owner_bedrooms = forms.ChoiceField(choices=BEDROOM_CHOICES, required=False)
    owner_bathrooms = forms.ChoiceField(choices=BATHROOM_CHOICES, required=False)

    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ('preferred_district',)
        widgets = {'customer_type': forms.Select(), 'property_description': forms.Textarea(attrs={'rows': 3}), 'owner_requirements': forms.Textarea(attrs={'rows': 3}), 'notes': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_agent'].queryset = User.objects.filter(is_active=True)
        for field_name in ('minimum_budget', 'budget'):
            if not getattr(self.instance, field_name, None):
                self.initial[field_name] = ''
        if self.instance and self.instance.pk:
            self.initial['requirements'] = [x.strip() for x in self.instance.requirements.split(',') if x.strip()]

    def clean_minimum_budget(self):
        return self.cleaned_data.get('minimum_budget') or Decimal('0')

    def clean_budget(self):
        return self.cleaned_data.get('budget') or Decimal('0')

    def clean_requirements(self):
        return ', '.join(self.cleaned_data.get('requirements', []))
