from django.shortcuts import render, get_object_or_404, redirect
from .models import Produto
from .forms import ProdutoForm
from usuario.models import Perfil
from django.contrib.auth.decorators import login_required

@login_required
def criar_produto(request):
    perfil = Perfil.objects.get(user=request.user)

    if perfil.role != 'cantineiro':
        return redirect('listar_produtos')  # redireciona alunos ou outros usuários

    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.save()  # salvando produto no banco
            return redirect('listar_produtos')
    else:
        form = ProdutoForm()

    return render(request, 'form.html', {'form': form, 'titulo': 'Criar Produto'})


@login_required
def editar_produto(request, produto_id):
    perfil = Perfil.objects.get(user=request.user)
    if perfil.role != 'cantineiro':
        return redirect('listar_produtos')  # redireciona usuários não cantineiros

    produto = get_object_or_404(Produto, id=produto_id)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('listar_produtos')
    else:
        form = ProdutoForm(instance=produto)

    return render(request, 'form.html', {'form': form, 'titulo': 'Editar Produto'})

def listar_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'produtos.html', {'produtos': produtos})