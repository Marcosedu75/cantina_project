from django.contrib import admin
from .models import Categoria
from .models import Produto

admin.site.register(Categoria)
admin.site.register(Produto)

# Register your models here.
