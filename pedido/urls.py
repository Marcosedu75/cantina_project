from django.urls import path
from . import views

urlpatterns = [
    path('listar/', views.listar_pedidos, name='listar'),
    path('detalhe/<int:pedido_id>/', views.detalhe_pedido, name='detalhe_pedido'),
    path('atualizar-status/<int:pedido_id>/', views.atualizar_status, name='atualizar_status'),
    path('deletar/<int:pedido_id>/', views.deletar_pedido, name='deletar_pedido'),
    path('historico/', views.historico_pedidos, name='historico_pedidos'),
    path('cardapio/', views.ver_cardapio, name='ver_cardapio'),
    # --- URLs do Carrinho ---
    path('carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/remover/<int:produto_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('carrinho/finalizar/', views.finalizar_pedido_carrinho, name='finalizar_pedido_carrinho'),
    path('carrinho/confirmar/', views.confirmar_pedido, name='confirmar_pedido'),
]