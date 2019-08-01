from django.contrib.auth.models import User
from django import forms


class RegistrationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }
        help_texts = {
            'username': None,
        }
