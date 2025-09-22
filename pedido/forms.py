from django import forms
from .models import Pedido

class AtualizarStatusForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['status']