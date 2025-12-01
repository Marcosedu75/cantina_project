from django.urls import path
from .views import listar_produtos, criar_produto, editar_produto, adicionar_estoque, remover_estoque, deletar_produto

urlpatterns = [
    path('listar_produto/', listar_produtos, name='listar_produtos'),
    path('novo/', criar_produto, name='criar_produto'),
    path('editar/<int:produto_id>/', editar_produto, name='editar_produto'),
    path('adicionar-estoque/<int:produto_id>/', adicionar_estoque, name='adicionar_estoque'),
    path('remover-estoque/<int:produto_id>/', remover_estoque, name='remover_estoque'),
    path('deletar/<int:produto_id>/', deletar_produto, name='deletar_produto'),
]
