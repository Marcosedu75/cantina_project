# usuario/admin.py
from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_editable = ('role',)  # permite mudar a role diretamente na listagem
