# usuario/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Perfil
from .models import Usuario

class CadastroForm(forms.ModelForm):
    ROLE_CHOICES = (
        ('aluno', 'Aluno'),
        ('cantineiro', 'Cantineiro'),
    )

    password = forms.CharField(widget=forms.PasswordInput, label='Senha')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirmar Senha')
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Tipo de Usuário')


    class Meta:
        model = User
        fields = ['username', 'email'] # Remova 'password' daqui, já que o campo personalizado foi adicionado

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError("As senhas não coincidem.")
        return password_confirm

    def save(self, commit=True):
        # Cria o usuário
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            # Cria o perfil associado com a role
            Perfil.objects.create(
                user=user,
                role=self.cleaned_data['role']
            )

        return user


class LoginForm(forms.Form):
    username = forms.CharField(label='Usuário')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['foto']