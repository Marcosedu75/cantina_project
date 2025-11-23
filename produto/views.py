from django.shortcuts import render, get_object_or_404, redirect
from .models import Produto, Categoria
from .forms import ProdutoForm
from usuario.models import Usuario
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib import messages
from urllib.parse import urlencode
from django.contrib.auth.models import User
from django.http import JsonResponse
from usuario.views import is_cantineiro, is_aluno


@user_passes_test(is_cantineiro, login_url='usuario_login')
def criar_produto(request):
    if request.method == 'POST':
        # Coleta dos dados
        nome = request.POST.get('nome')
        preco_str = request.POST.get('preco')
        estoque = request.POST.get('estoque')
        categoria_nome = request.POST.get('categoria', '').strip()
        foto = request.FILES.get('foto')
        
        # --- LÓGICA DE CONVERSÃO DO PREÇO ---
        # Substitui a vírgula por ponto, se existir
        preco = 0
        if preco_str:
            preco = preco_str.replace(',', '.')
        # ------------------------------------

        # Verifica se estoque está vazio e define 0
        if estoque is None or estoque == '':
            estoque = 0

        # Trata categoria: busca ignorando maiúsculas/minúsculas ou cria nova
        categoria_obj = Categoria.objects.filter(nome__iexact=categoria_nome).first()
        if not categoria_obj and categoria_nome:
            categoria_obj = Categoria.objects.create(nome=categoria_nome)

        # Cria o produto
        Produto.objects.create(
            nome=nome,
            preco=preco,
            estoque=estoque,
            categoria=categoria_obj,
            foto=foto
        )
        messages.success(request, f"Produto '{nome}' criado com sucesso!")
        return redirect('listar_produtos')

    return render(request, 'criar_produto.html')


@user_passes_test(is_cantineiro, login_url='usuario_login')
def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    if request.method == 'POST':
        # Coleta manual dos dados do formulário e atualiza o objeto
        produto.nome = request.POST.get('nome')
        
        # --- LÓGICA DE CONVERSÃO DO PREÇO (EDIÇÃO) ---
        preco_str = request.POST.get('preco')
        if preco_str:
            produto.preco = preco_str.replace(',', '.')
        # -------------------------------------------

        produto.estoque = request.POST.get('estoque')
        categoria_nome = request.POST.get('categoria', '').strip()
        
        # Lógica para buscar ou criar a categoria
        if categoria_nome:
            categoria_obj, created = Categoria.objects.get_or_create(
                nome__iexact=categoria_nome,
                defaults={'nome': categoria_nome}
            )
            produto.categoria = categoria_obj
        else:
            # Se o nome da categoria for apagado, remove a associação
            produto.categoria = None

        # Verifica se a remoção da foto foi solicitada
        if request.POST.get('remover_foto'):
            produto.foto.delete(save=False) # Deleta o arquivo
            produto.foto = None # Remove a referência no modelo

        # Verifica se uma nova foto foi enviada
        if 'foto' in request.FILES:
            produto.foto = request.FILES['foto']
        
        produto.save()
        # Adiciona uma mensagem de sucesso
        messages.success(request, 'Produto salvo com sucesso!')
        return redirect('editar_produto', produto_id=produto.id)

    # Adicione o produto no contexto para o template
    return render(request, 'editar_produto.html', {
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
        messages.success(request, f"Produto '{produto.nome}' excluído com sucesso!")
        return redirect('listar_produtos')
        
    
    
    return render(request, 'confirm_delete.html', {'produto': produto})
