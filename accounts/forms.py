from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'role',
            'is_active'
        ]

    def clean_username(self):
        username = self.cleaned_data['username']
        users = User.objects.filter(username__iexact=username)

        if self.instance.pk:
            users = users.exclude(pk=self.instance.pk)

        if users.exists():
            raise forms.ValidationError(
                'This username already exists.'
            )

        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user