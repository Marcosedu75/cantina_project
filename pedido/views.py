from django.shortcuts import render, get_object_or_404, redirect
from .models import Pedido, ItemPedido, Produto
from usuario.models import Usuario
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import AtualizarStatusForm
from usuario.views import is_cantineiro, is_aluno

# DUMMY_PEDIDOS = {
#     'pedido1': {
#         'id': 1,
#         'itens': [],
#         'total': 10.00,
#     },
#     'pedido2': {
#         'nome': 'marcos',
#         'id': 2,
#         'itens': [],
#         'total': 20.00, },

# }

@user_passes_test(is_cantineiro, login_url='login')
def listar_pedidos(request):
    pedidos = Pedido.objects.prefetch_related('usuario').order_by('-data_pedido')
    #pedidos = DUMMY_PEDIDOS.values()  # Usar .values() para iterar sobre os valores do dicionário
    return render(request, 'listar.html', {'pedidos': pedidos})

@user_passes_test(is_cantineiro, login_url='login')
def detalhe_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    itens = pedido.itens.select_related('produto')
    return render(request, 'detalhe.html', {'pedido': pedido, 'itens': itens})

@user_passes_test(is_cantineiro, login_url='login')
def atualizar_status(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        form = AtualizarStatusForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            return redirect('listar')
    else:
        form = AtualizarStatusForm(instance=pedido)
    return render(request, 'atualizar_status.html', {'form': form, 'pedido': pedido})

@user_passes_test(is_cantineiro, login_url='login')
def deletar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        # Itera sobre cada item do pedido e chama o método .delete() de cada um.
        # Isso garante que a sua lógica customizada em ItemPedido.delete() seja executada.
        for item in pedido.itens.all():
            item.delete()

        # Agora que os itens foram removidos e o estoque devolvido,
        # podemos deletar o objeto Pedido, que agora está vazio.
        pedido.delete()
        return redirect('listar')
    return render(request, 'pedido/delete.html', {'pedido': pedido})

    #aluno


@user_passes_test(is_aluno, login_url='login')
def criar_pedidos(request):
    """
    Exibe o cardápio para o usuário fazer um novo pedido (GET)
    e processa o pedido enviado (POST).
    """

    # Busca produtos com estoque para exibir no cardápio (GET) e processar o pedido (POST)
    produtos = Produto.objects.filter(estoque__gt=0)

    if request.method == 'POST':
        itens_selecionados = []
        valor_total_pedido = 0

        # Etapa 1: Validar o pedido e calcular o total
        for produto in produtos:
            quantidade_str = request.POST.get(f'item_{produto.id}')
            if quantidade_str and int(quantidade_str) > 0:
                quantidade = int(quantidade_str)

                # Validação de estoque
                if quantidade > produto.estoque:
                    # Adiciona uma mensagem de erro e recarrega a página
                    context = {
                        'cardapio': produtos,
                        'erro': f"Estoque insuficiente para '{produto.nome}'. Apenas {produto.estoque} unidades disponíveis."
                    }
                    return render(request, 'criar_pedidos.html', context)

                itens_selecionados.append({
                    'produto': produto,
                    'quantidade': quantidade,
                    'preco_unitario': produto.preco
                })
                valor_total_pedido += produto.preco * quantidade

        # Etapa 2: Salvar o pedido no banco de dados se houver itens
        if itens_selecionados:
            # Cria o pedido principal
            novo_pedido = Pedido.objects.create(
                usuario=request.user,
                valor_total=valor_total_pedido
            )

            # Cria os itens do pedido e atualiza o estoque
            for item_data in itens_selecionados:
                ItemPedido.objects.create(pedido=novo_pedido, **item_data)
                produto = item_data['produto']
                produto.estoque -= item_data['quantidade']
                produto.save()

            return redirect('historico_pedidos') # Redireciona para o histórico

    context = {'cardapio': produtos}  # Passa os produtos para o contexto
    return render(request, 'criar_pedidos.html', context)

@user_passes_test(is_aluno, login_url='login')
def historico_pedidos(request):
    # Busca os pedidos do usuário logado, do mais recente para o mais antigo
    pedidos_do_usuario = Pedido.objects.filter(usuario=request.user).order_by('-data_pedido')
    context = {'pedidos': pedidos_do_usuario}
    return render(request, 'historico_pedidos.html', context)

@user_passes_test(is_aluno, login_url='login')
def ver_cardapio(request):
    """
    Exibe um cardápio visual para o aluno, mostrando apenas produtos com estoque.
    """
    query = request.GET.get('q', '')
    # A view agora está em 'pedido', então precisa importar 'Produto'
    produtos = Produto.objects.filter(estoque__gt=0)
    if query:
        produtos = produtos.filter(nome__icontains=query)
    
    return render(request, 'ver_cardapio.html', {'produtos': produtos, 'query': query})

# --- FUNCIONALIDADES DO CARRINHO ---

@user_passes_test(is_aluno, login_url='login')
def adicionar_ao_carrinho(request, produto_id):
    """ Adiciona um produto ao carrinho na sessão. """
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho = request.session.get('carrinho', {})
    quantidade_str = request.POST.get('quantidade', '1')
    quantidade = int(quantidade_str) if quantidade_str.isdigit() and int(quantidade_str) > 0 else 1

    id_produto_str = str(produto.id)

    # Verifica o estoque antes de adicionar
    quantidade_atual_no_carrinho = carrinho.get(id_produto_str, 0)
    if (quantidade_atual_no_carrinho + quantidade) > produto.estoque:
        messages.error(request, f"Estoque insuficiente para '{produto.nome}'. Disponível: {produto.estoque}")
    else:
        carrinho[id_produto_str] = quantidade_atual_no_carrinho + quantidade
        request.session['carrinho'] = carrinho
        messages.success(request, f"{quantidade}x '{produto.nome}' adicionado(s) ao carrinho.")

    return redirect('ver_cardapio')

@user_passes_test(is_aluno, login_url='login')
def ver_carrinho(request):
    """ Exibe os itens do carrinho. """
    carrinho_session = request.session.get('carrinho', {})
    itens_carrinho = []
    valor_total = 0

    # Busca os produtos do carrinho no banco de dados de uma só vez
    produtos_no_carrinho = Produto.objects.filter(id__in=carrinho_session.keys())

    for produto in produtos_no_carrinho:
        quantidade = carrinho_session[str(produto.id)]
        subtotal = produto.preco * quantidade
        itens_carrinho.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal,
        })
        valor_total += subtotal

    return render(request, 'carrinho.html', {'itens_carrinho': itens_carrinho, 'valor_total': valor_total})

@user_passes_test(is_aluno, login_url='login')
def remover_do_carrinho(request, produto_id):
    """ Remove um item do carrinho. """
    carrinho = request.session.get('carrinho', {})
    id_produto_str = str(produto_id)

    if id_produto_str in carrinho:
        del carrinho[id_produto_str]
        request.session['carrinho'] = carrinho
        messages.success(request, "Item removido do carrinho.")

    return redirect('ver_carrinho')

@user_passes_test(is_aluno, login_url='login')
def finalizar_pedido_carrinho(request):
    """
    Exibe a página de seleção de pagamento com o total do carrinho.
    """
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('ver_carrinho')

    # Apenas calcula o total e renderiza a página de seleção de pagamento
    produtos_no_carrinho = Produto.objects.filter(id__in=carrinho.keys())
    valor_total_pedido = sum(p.preco * carrinho[str(p.id)] for p in produtos_no_carrinho)

    context = {'valor_total': valor_total_pedido}
    return render(request, 'selecionar_pagamento.html', context)

@user_passes_test(is_aluno, login_url='login')
def confirmar_pedido(request):
    """
    Processa o POST da página de pagamento, cria o pedido e limpa o carrinho.
    """
    if request.method != 'POST':
        # Se não for POST, redireciona para o carrinho, pois não há o que confirmar.
        return redirect('ver_carrinho')

    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('ver_carrinho')

    produtos_no_carrinho = Produto.objects.filter(id__in=carrinho.keys())
    valor_total_pedido = sum(p.preco * carrinho[str(p.id)] for p in produtos_no_carrinho)
    forma_pagamento = request.POST.get('pagamento', 'dinheiro')

    novo_pedido = Pedido.objects.create(usuario=request.user, valor_total=valor_total_pedido, pagamento=forma_pagamento)

    for produto in produtos_no_carrinho:
        quantidade = carrinho[str(produto.id)]
        ItemPedido.objects.create(pedido=novo_pedido, produto=produto, quantidade=quantidade, preco_unitario=produto.preco)
        produto.estoque -= quantidade
        produto.save()

    del request.session['carrinho']
    messages.success(request, "Pedido finalizado com sucesso!")
    return redirect('historico_pedidos')