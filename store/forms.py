from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

# Modello per la registrazione dell'utente
class CustomerRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'first_name' in self.fields:
            self.fields['first_name'].required = True
            self.fields['first_name'].label = "Nome"
        if 'last_name' in self.fields:
            self.fields['last_name'].required = True
            self.fields['last_name'].label = "Cognome"
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'