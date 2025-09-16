from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_pedidos, name='listar_pedidos'),
    path('<int:pedido_id>/', views.detalhe_pedido, name='detalhe_pedido'),
    path('<int:pedido_id>/atualizar/', views.atualizar_status, name='atualizar_status'),
    path('<int:pedido_id>/deletar/', views.deletar_pedido, name='deletar_pedido'),
]