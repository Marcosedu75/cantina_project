from django.urls import path
from . import views

urlpatterns = [
    path('listar/', views.listar_pedidos, name='listar'),
    path('detalhe/<int:pedido_id>/', views.detalhe_pedido, name='detalhe_pedido'),
    path('atualizar-status/<int:pedido_id>/', views.atualizar_status, name='atualizar_status'),
    path('deletar/<int:pedido_id>/', views.deletar_pedido, name='deletar_pedido'),
    path('novo/', views.criar_pedidos, name='criar_pedidos'),
    path('historico/', views.historico_pedidos, name='historico_pedidos'),
    path('cardapio/', views.ver_cardapio, name='ver_cardapio'),
]