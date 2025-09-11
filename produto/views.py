from django.shortcuts import render, get_object_or_404, redirect
from .models import Produto
from .forms import ProdutoForm
from usuario.models import Usuario
from django.contrib.auth.decorators import login_required

def criar_produto(request):
    form = ProdutoForm(request.POST or None)
    produto = None  # garante que existe mesmo se GET
    
    if form.is_valid():
        produto = form.save()
        return redirect('listar_produtos')
    
    return render(request, 'form.html', {'form': form, 'titulo': 'Editar Produto', 'produto': produto})


@login_required
def editar_produto(request, produto_id):
    usuario = get_object_or_404(Usuario, user=request.user)

    if usuario.role != 'cantineiro':
        return redirect('listar_produtos')

    produto = get_object_or_404(Produto, id=produto_id)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('listar_produtos')
    else:
        form = ProdutoForm(instance=produto)

    # Adicione o produto no contexto para o template
    return render(request, 'form.html', {
        'form': form,
        'titulo': 'Editar Produto',
        'produto': produto
    })


@login_required
def listar_produtos(request):
    usuario = get_object_or_404(Usuario, user=request.user)

    if usuario.role == 'cantineiro':
        # ✅ Cantineiro só vê os produtos que ele mesmo criou
        produtos = Produto.objects.all()
    else:
        # ✅ Alunos e outros perfis veem todos
        produtos = Produto.objects.all()

    return render(request, 'produtos.html', {'produtos': produtos, 'perfil': usuario})


@login_required
def adicionar_estoque(request, produto_id):
    usuario = get_object_or_404(Usuario, user=request.user)
    
    if usuario.role != 'cantineiro':
        return redirect('listar_produtos')
    
    # Agora qualquer cantineiro pode adicionar estoque em qualquer produto
    produto = get_object_or_404(Produto, id=produto_id)
    produto.estoque += 1
    produto.save()
    
    return redirect('listar_produtos')


@login_required
def remover_estoque(request, produto_id):
    usuario = get_object_or_404(Usuario, user=request.user)
    
    if usuario.role != 'cantineiro':
        return redirect('listar_produtos')
    
    # Agora qualquer cantineiro pode remover estoque de qualquer produto
    produto = get_object_or_404(Produto, id=produto_id)
    
    if produto.estoque > 0:
        produto.estoque -= 1
        produto.save()
    
    return redirect('listar_produtos')

@login_required
def deletar_produto(request, produto_id):
    usuario = get_object_or_404(Usuario, user=request.user)
    
    if usuario.role != 'cantineiro':
        return redirect('listar_produtos')
    
    produto = get_object_or_404(Produto, id=produto_id)
    
    if request.method == "POST":
        produto.delete()
        return redirect('listar_produtos')
    
    return render(request, 'confirm_delete.html', {'produto': produto})
