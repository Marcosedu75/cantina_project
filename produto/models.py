from django.db import models
from usuario.models import Perfil


class Categoria(models.Model):
    nome = models.CharField(max_length=100, blank=False, null=False)
    slug = models.SlugField(unique=True, blank=False, null=False)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=100, blank=False, null=False)
    slug = models.SlugField(unique=True, blank=False, null=False)
    preco = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="produtos", blank=False, null=False)
    estoque = models.IntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return self.nome