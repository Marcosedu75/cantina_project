from django.urls import path
from .views import criar_produto, listar_produtos, editar_produto

urlpatterns = [
    path('', listar_produtos, name='listar_produtos'),
    path('novo/', criar_produto, name='criar_produto'),
    path('editar/<int:produto_id>/', editar_produto, name='editar_produto'),
]