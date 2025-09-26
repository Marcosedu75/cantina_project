# usuario/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Usuario

class CadastroForm(forms.ModelForm):
    full_name = forms.CharField(label='Nome Completo', max_length=181, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, label='Senha')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirmar Senha')
    

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email']

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


    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if len(full_name.split()) < 2:
            raise ValidationError("Por favor, insira seu nome e sobrenome.")
        return full_name

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data['full_name'].split()
        user.first_name = full_name[0]
        user.last_name = ' '.join(full_name[1:])
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
