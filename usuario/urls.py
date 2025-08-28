# usuario/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import cadastro_view, home_view, login_view, login_redirect_view, logout_view, gerenciar_pedidos_view, produtos, fazer_pedido
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', home_view, name='home'),
    path('cadastro/', cadastro_view, name='cadastro_view'),
    path('login/', login_view, name='login'),
    path('dashboard/cantineiro/', login_redirect_view, name='dashboard_cantineiro'),
    path('logout/', logout_view, name='logout'),
    path('gerenciamento/', gerenciar_pedidos_view, name='gerenciar_pedidos'),
    path('produtos/', produtos, name='produtos'),
    path('fazerpedido/', fazer_pedido, name='fazer_pedido')

]




