from django.contrib import admin
from django.urls import path, include
from usuario.views import home_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('usuario/', include('usuario.urls')),  # Aqui incluímos a app usuario
    path('produtos/', include('produto.urls')), 
    path('pedidos/', include('pedido.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)