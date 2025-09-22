from django.db import models
from django.conf import settings
from produto.models import Produto
from usuario.models import Usuario


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('pendente', 'Pendente'),
        ('preparo', 'Em Preparo'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pedidos")
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    valor_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    pagamento = models.CharField(
        max_length=20,
        choices=[('dinheiro', 'Dinheiro'), ('cartao', 'Cartão de Crédito/Débito')],
        default='dinheiro'
    )

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=6, decimal_places=2)

    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} (Pedido {self.pedido.id})"

    def delete(self, *args, **kwargs):
        # Devolve a quantidade ao estoque do produto antes de deletar o item
        self.produto.estoque += self.quantidade
        self.produto.save()
        # Chama o método delete original
        super().delete(*args, **kwargs)


