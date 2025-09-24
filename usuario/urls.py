# usuario/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import cadastro_view, login_view, logout_view, gerenciar_pedidos_view, produtos, fazer_pedido, usuario, deletar_conta, login_redirect_view, dashboard_cantineiro, painel_usuario
from django.contrib.auth.views import LogoutView


urlpatterns = [
    
    path('cadastro/', cadastro_view, name='cadastro_view'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('gerenciamento/', gerenciar_pedidos_view, name='gerenciar_pedidos'),
    path('produtos/', produtos, name='produtos'),
    path('fazerpedido/', fazer_pedido, name='fazer_pedido'),
    path('usuario/', usuario, name='usuario'),
    path('deletarconta/', deletar_conta, name='deletar_conta'),
    path('poslogin/', login_redirect_view, name='login_redirect'),
    path('painel-cantineiro/', dashboard_cantineiro, name='dashboard_cantineiro'),
    path('painel/', painel_usuario, name='painel_usuario'),


]




