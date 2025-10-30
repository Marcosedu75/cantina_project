from django.shortcuts import render, get_object_or_404, redirect
from .models import Produto
from .forms import ProdutoForm
from usuario.models import Usuario
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from urllib.parse import urlencode
from django.contrib.auth.models import User
from django.http import JsonResponse
from usuario.views import is_cantineiro, is_aluno


@user_passes_test(is_cantineiro, login_url='usuario_login')
def criar_produto(request):
    if request.method == 'POST':
        # Para upload de arquivos, é crucial passar request.FILES
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_produtos')
    else:
        form = ProdutoForm()

    # O título deve ser 'Criar Produto' aqui
    return render(request, 'form.html', {'form': form, 'titulo': 'Criar Produto'})


@user_passes_test(is_cantineiro, login_url='usuario_login')
def editar_produto(request, produto_id):
    usuario = get_object_or_404(Usuario, user=request.user)

    if usuario.role != 'cantineiro':
        return redirect('listar_produtos')

    produto = get_object_or_404(Produto, id=produto_id)

    if request.method == 'POST':
        # Também precisa de request.FILES para o caso de a foto ser alterada
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
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
    query = request.GET.get('q', '')

    if usuario.role == 'cantineiro':
        produtos = Produto.objects.all()


    else:
        produtos = Produto.objects.filter(estoque__gt=0)

    if query:
        produtos = produtos.filter(nome__icontains=query)

    # Se a requisição for AJAX, retorna os dados em formato JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Converte o queryset de produtos para uma lista de dicionários
        produtos_data = list(produtos.values('id', 'nome', 'preco', 'estoque', 'foto', 'categoria__nome'))
        # Adiciona a URL da foto completa
        for produto in produtos_data:
            if produto['foto']:
                produto['foto_url'] = request.build_absolute_uri(f'/media/{produto["foto"]}')
            else:
                produto['foto_url'] = None
        return JsonResponse({'produtos': produtos_data})

    return render(request, 'produtos.html', {'produtos': produtos, 'perfil': usuario, 'query': query})
    

@user_passes_test(is_cantineiro, login_url='usuario_login')
def adicionar_estoque(request, produto_id):
    usuario = get_object_or_404(Usuario, user=request.user)
    if usuario.role != 'cantineiro':
        return redirect('listar_produtos')
    produto = get_object_or_404(Produto, id=produto_id)
    produto.estoque += 1
    produto.save()

    q = request.GET.get('q')
    url = reverse('listar_produtos')
    if q:
        url += '?' + urlencode({'q': q})
    return redirect(url)

@user_passes_test(is_cantineiro, login_url='usuario_login')
def remover_estoque(request, produto_id):
    usuario = get_object_or_404(Usuario, user=request.user)
    if usuario.role != 'cantineiro':
        return redirect('listar_produtos')
    produto = get_object_or_404(Produto, id=produto_id)
    if produto.estoque > 0:
        produto.estoque -= 1
        produto.save()

    q = request.GET.get('q')
    url = reverse('listar_produtos')
    if q:
        url += '?' + urlencode({'q': q})
    return redirect(url)

@user_passes_test(is_cantineiro, login_url='usuario_login')
def deletar_produto(request, produto_id):
    usuario = get_object_or_404(Usuario, user=request.user)
    
    if usuario.role != 'cantineiro':
        return redirect('listar_produtos')
    
    produto = get_object_or_404(Produto, id=produto_id)
    
    if request.method == "POST":
        produto.delete()
        return redirect('listar_produtos')
    
    return render(request, 'confirm_delete.html', {'produto': produto})
