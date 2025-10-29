from django.shortcuts import render, get_object_or_404, redirect
from .models import Pedido, ItemPedido, Produto
from usuario.models import Usuario
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
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
    produtos_qs = Produto.objects.filter(estoque__gt=0)
    if query:
        produtos_qs = produtos_qs.filter(nome__icontains=query)
    
    # Calcula o valor total do carrinho atual
    carrinho_session = request.session.get('carrinho', {})
    valor_total_carrinho = 0
    if carrinho_session:
        # Busca os produtos do carrinho no banco de dados de uma só vez
        produtos_no_carrinho = Produto.objects.filter(id__in=carrinho_session.keys())
        for produto in produtos_no_carrinho:
            quantidade = carrinho_session.get(str(produto.id), 0)
            valor_total_carrinho += produto.preco * quantidade

    context = {
        'produtos': produtos_qs, 
        'query': query,
        'valor_total_carrinho': valor_total_carrinho
    }

    return render(request, 'ver_cardapio.html', context)

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
        link_carrinho = f'<a href="{reverse("ver_carrinho")}" class="alert-link">Ir para o carrinho</a>'
        messages.success(request, f"'{produto.nome}' adicionado. {link_carrinho}")

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

@user_passes_test(is_aluno, login_url='login')
def cancelar_pedido_aluno(request, pedido_id):
    """
    Permite que um aluno cancele seu próprio pedido se o status for
    'aberto' ou 'pendente'.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    if request.method == 'POST':
        # Verifica se o pedido pode ser cancelado
        if pedido.status in ['aberto', 'pendente']:
            pedido_id_msg = pedido.id

            # 1. Devolve os itens ao estoque ANTES de deletar
            for item in pedido.itens.all():
                item.produto.estoque += item.quantidade
                item.produto.save()
            
            # 2. Agora deleta o pedido com segurança
            pedido.delete()
            messages.success(request, f"Pedido #{pedido_id_msg} foi cancelado e removido com sucesso.")
        else:
            messages.error(request, f"Não é possível cancelar o pedido #{pedido.id}, pois ele já está '{pedido.get_status_display()}'.")
    
    return redirect('historico_pedidos')