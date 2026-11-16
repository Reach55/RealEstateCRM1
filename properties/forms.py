
from django import forms
from .models import Property


PHNOM_PENH_DISTRICTS = [
    ('Chamkar Mon', 'Chamkar Mon'),
    ('Doun Penh', 'Doun Penh'),
    ('Prampir Makara', 'Prampir Makara'),
    ('Tuol Kouk', 'Tuol Kouk'),
    ('Dangkao', 'Dangkao'),
    ('Mean Chey', 'Mean Chey'),
    ('Russey Keo', 'Russey Keo'),
    ('Sen Sok', 'Sen Sok'),
    ('Pou Senchey', 'Pou Senchey'),
    ('Chroy Changvar', 'Chroy Changvar'),
    ('Prek Pnov', 'Prek Pnov'),
    ('Chbar Ampov', 'Chbar Ampov'),
    ('Boeng Keng Kang', 'Boeng Keng Kang'),
    ('Kamboul', 'Kamboul'),
]


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            return []
        return [super(MultipleFileField, self).clean(item, initial) for item in data]


class PropertyForm(forms.ModelForm):
    photos = MultipleFileField(required=False, help_text='Select additional property photos.')
    image = forms.ImageField(
        label='House photo',
        widget=forms.ClearableFileInput(attrs={
            'accept': 'image/*',
            'capture': 'environment',
        }),
    )
    location = forms.ChoiceField(
        label='Location',
        choices=[('', 'Select a Phnom Penh district'), *PHNOM_PENH_DISTRICTS],
        widget=forms.Select(),
    )

    class Meta:
        model = Property

        fields = [
            'title',
            'listing_type',
            'property_type',
            'price',
            'monthly_rent',
            'location',
            'owner',
            'agent',
            'bedrooms',
            'bathrooms',
            'area',
            'land_size',
            'house_size',
            'description',
            'image',
            'photos',
            'features',
            'swimming_pool',
            'parking',
            'garden',
            'furnished',
            'status',
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'features': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = not bool(self.instance.image)
        self.fields['image'].help_text = 'Take a photo or upload a clear image of the house.'

    def save(self, commit=True):
        property_obj = super().save(commit=False)
        property_obj.city = 'Phnom Penh'
        property_obj.district = property_obj.location
        property_obj.commune = ''
        if commit:
            property_obj.save()
            self.save_m2m()
        return property_obj
