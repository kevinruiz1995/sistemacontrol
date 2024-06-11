from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.safestring import mark_safe

class CustomLoginForm(AuthenticationForm):

    # Personaliza el campo de nombre de usuario (username)
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario','autocomplete':'username', 'col':'col-md-12'  }),
        )

    # Personaliza el campo de contraseña (password)
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'contraseña','autocomplete':'current-password','col':'col-md-12'}),
    )


    # # Personaliza los mensajes de error si es necesario
    # error_messages = {
    #     'invalid_login': 'Nombre de usuario o contraseña incorrectos.',
    #     'inactive': 'Tu cuenta está desactivada. Por favor, contacta al administrador.',
    # }






class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name')
