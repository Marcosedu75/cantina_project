# usuario/admin.py
from django.contrib import admin
from .models import Perfil, Usuario

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_editable = ('role',)  # permite mudar a role diretamente na listagem
