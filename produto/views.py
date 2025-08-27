from django.shortcuts import render
from usuario.models import Perfil
from .forms import ProdutoForm
from django.shortcuts import get_object_or_404

def criar_produto(request):
    perfil = Perfil.objects.get(user=request.user)
    if perfil.role != 'cantineiro':
        return redirect('listar_produtos')  # ou exibir erro

    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.criado_por = perfil
            produto.save()
            return redirect('listar_produtos')
    else:
        form = ProdutoForm()
    return render(request, 'produto/form.html', {'form': form})

def listar_produtos(request):
    perfil = Perfil.objects.get(user=request.user)

    if perfil.role == 'cantineiro':
        produtos = Produto.objects.filter(criado_por=perfil)
    else:
        produtos = Produto.objects.filter(estoque__gt=0)

    return render(request, 'listar.html', {'produtos': produtos})

def editar_produto(request, produto_id):
    perfil = Perfil.objects.get(user=request.user)
    produto = get_object_or_404(Produto, id=produto_id, criado_por=perfil)

    form = ProdutoForm(request.POST or None, instance=produto)
    if form.is_valid():
        form.save()
        return redirect('listar_produtos')

    return render(request, 'produto/form.html', {'form': form})

# Create your views here.
