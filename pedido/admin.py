from django.contrib import admin
from django.urls import path, include
from .models import Pedido, ItemPedido

# Register your models here.
admin.site.register(Pedido)
admin.site.register(ItemPedido)