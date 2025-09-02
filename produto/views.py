from django.shortcuts import render, get_object_or_404, redirect
from .models import Produto
from .forms import ProdutoForm
from usuario.models import Perfil
from django.contrib.auth.decorators import login_required

@login_required
def criar_produto(request):
    perfil = get_object_or_404(Perfil, user=request.user)

    if perfil.role != 'cantineiro':
        return redirect('listar_produtos')

    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.criado_por = request.user  # ✅ agora associa ao User
            produto.save()
            return redirect('listar_produtos')
    else:
        form = ProdutoForm()

    return render(request, 'form.html', {'form': form, 'titulo': 'Criar Produto'})

@login_required
def editar_produto(request, produto_id):
    perfil = get_object_or_404(Perfil, user=request.user)

    if perfil.role != 'cantineiro':
        return redirect('listar_produtos')

    # Garante que o cantineiro só possa editar seus próprios produtos
    produto = get_object_or_404(Produto, id=produto_id, criado_por=request.user)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('listar_produtos')
    else:
        form = ProdutoForm(instance=produto)

    return render(request, 'form.html', {'form': form, 'titulo': 'Editar Produto'})

@login_required
def listar_produtos(request):
    perfil = get_object_or_404(Perfil, user=request.user)

    if perfil.role == 'cantineiro':
        # ✅ Cantineiro só vê os produtos que ele mesmo criou
        produtos = Produto.objects.filter(criado_por=request.user)
    else:
        # ✅ Alunos e outros perfis veem todos
        produtos = Produto.objects.all()

    return render(request, 'produtos.html', {'produtos': produtos, 'perfil': perfil})
