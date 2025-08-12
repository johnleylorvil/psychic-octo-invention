from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(UserCreationForm):
    """
    Formulaire d'inscription personnalisé pour étendre le UserCreationForm
    avec les champs de votre modèle User.
    """
    first_name = forms.CharField(max_length=30, required=True, help_text='Prénom requis.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Nom de famille requis.')
    email = forms.EmailField(max_length=254, required=True, help_text='Adresse e-mail requise.')
    phone = forms.CharField(max_length=20, required=True, help_text='Numéro de téléphone requis.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        if commit:
            user.save()
        return user