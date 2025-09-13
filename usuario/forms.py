# usuario/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Usuario

class CadastroForm(forms.ModelForm):
    first_name = forms.CharField(label='Nome', max_length=30, required=True)
    last_name = forms.CharField(label='Sobrenome', max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, label='Senha')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirmar Senha')
    

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise ValidationError("As senhas não coincidem.")
        return password_confirm


    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            Usuario.objects.create(
                user=user,
                role='aluno'
            )
        return user
        


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['foto']
