from django.shortcuts import render, get_object_or_404, redirect
from .models import Pedido, ItemPedido, Produto
from usuario.models import Usuario
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib import messages
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

@user_passes_test(is_cantineiro, login_url='usuario_login')
def listar_pedidos(request):
    # Exclui os pedidos com status 'aberto', que são os carrinhos dos usuários.
    pedidos = Pedido.objects.exclude(status='aberto').prefetch_related('usuario').order_by('-data_pedido')
    #pedidos = DUMMY_PEDIDOS.values()  # Usar .values() para iterar sobre os valores do dicionário
    return render(request, 'listar.html', {'pedidos': pedidos})

@user_passes_test(is_cantineiro, login_url='usuario_login')
def detalhe_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    itens = pedido.itens.select_related('produto')
    return render(request, 'detalhe.html', {'pedido': pedido, 'itens': itens})

@user_passes_test(is_cantineiro, login_url='usuario_login')
def atualizar_status(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        # REGRA DE NEGÓCIO: Impede a alteração de pedidos em estado final.
        if pedido.status in ['entregue', 'cancelado']:
            messages.error(request, f"O Pedido #{pedido.id} já foi '{pedido.get_status_display()}' e não pode ser alterado.")
            return redirect('atualizar_status', pedido_id=pedido.id)

        novo_status = request.POST.get('status')
        
        # Valida se o status recebido é uma das opções válidas no modelo Pedido
        opcoes_validas = [choice[0] for choice in Pedido.STATUS_CHOICES]
        if novo_status in opcoes_validas:
            pedido.status = novo_status
            pedido.save()
            messages.success(request, f"Status do Pedido #{pedido.id} atualizado para '{pedido.get_status_display()}'.")
            return redirect('atualizar_status', pedido_id=pedido.id)
        else:
            messages.error(request, "Status inválido. A atualização falhou.")
            # Redireciona de volta para a página de detalhes ou lista
            return redirect('detalhe_pedido', pedido_id=pedido.id)

    return render(request, 'atualizar_status.html', {'pedido': pedido, 'status_choices': Pedido.STATUS_CHOICES})
@user_passes_test(is_cantineiro, login_url='usuario_login')
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



@user_passes_test(is_aluno, login_url='usuario_login')
def historico_pedidos(request):
    # Busca os pedidos do usuário logado, do mais recente para o mais antigo
    pedidos_do_usuario = Pedido.objects.filter(usuario=request.user).order_by('-data_pedido')
    context = {'pedidos': pedidos_do_usuario}
    return render(request, 'historico_pedidos.html', context)

@user_passes_test(is_aluno, login_url='usuario_login')
def ver_cardapio(request):
    """
    Exibe um cardápio visual para o aluno, mostrando apenas produtos com estoque.
    """
    query = request.GET.get('q', '')
    # A view agora está em 'pedido', então precisa importar 'Produto'
    produtos_qs = Produto.objects.filter(estoque__gt=0)
    if query:
        produtos_qs = produtos_qs.filter(nome__icontains=query)
    
    # --- IMPLEMENTAÇÃO DO FIXME ---
    # Pega o pedido aberto do usuário (que a view de login já garante que exista)
    pedido_aberto = Pedido.objects.filter(usuario=request.user, status='aberto').first()

    # Monta a lista de itens para o template, combinando produto e quantidade
    itens_cardapio = []
    for produto in produtos_qs:
        quantidade = 0
        if pedido_aberto:
            # Busca o item correspondente a este produto dentro do pedido aberto
            item_no_pedido = ItemPedido.objects.filter(pedido=pedido_aberto, produto=produto).first()
            if item_no_pedido:
                quantidade = item_no_pedido.quantidade
        # Adiciona o produto e sua quantidade (0 se não estiver no pedido) à lista
        itens_cardapio.append({'produto': produto, 'quantidade': quantidade})

    context = {
        'itens_cardapio': itens_cardapio, 
        'query': query,
    }

    return render(request, 'ver_cardapio.html', context)

# --- FUNCIONALIDADES DO CARRINHO ---

@user_passes_test(is_aluno, login_url='usuario_login')
def adicionar_ao_carrinho(request, produto_id):
    """ Adiciona um produto ao pedido aberto (carrinho) no banco de dados. """
    produto = get_object_or_404(Produto, id=produto_id)
    
    # --- IMPLEMENTAÇÃO DO FIXME ---
    # Encontra o pedido aberto do usuário. A view de login já garante que ele exista.
    pedido_aberto, created = Pedido.objects.get_or_create(usuario=request.user, status='aberto')

    # Encontra o item no pedido ou cria um novo se não existir.
    item_pedido, created = ItemPedido.objects.get_or_create(
        pedido=pedido_aberto,
        produto=produto,
        defaults={'quantidade': 0, 'preco_unitario': produto.preco}
    )

    # Verifica o estoque antes de adicionar
    if (item_pedido.quantidade + 1) > produto.estoque:
        messages.error(request, f"Estoque insuficiente para '{produto.nome}'. Disponível: {produto.estoque}")
    else:
        # Aumenta a quantidade e salva no banco de dados
        item_pedido.quantidade += 1
        item_pedido.save()
        link_carrinho = f'<a href="{reverse("ver_carrinho")}" class="alert-link">Ir para o carrinho</a>'
        messages.success(request, f"'{produto.nome}' adicionado. {link_carrinho}", extra_tags='safe')

    return redirect('ver_cardapio')

@user_passes_test(is_aluno, login_url='usuario_login')
def ver_carrinho(request):
    """ Exibe os itens do carrinho. """
    # Busca o pedido aberto (carrinho) do usuário no banco de dados
    pedido_aberto = Pedido.objects.filter(usuario=request.user, status='aberto').first()
    itens_carrinho = []
    valor_total = 0

    if pedido_aberto:
        # Se o pedido existir, busca todos os itens dele
        itens_carrinho = pedido_aberto.itens.select_related('produto').all()
        # Calcula o valor total do pedido
        valor_total = sum(item.subtotal() for item in itens_carrinho)

    context = {
        'itens_carrinho': itens_carrinho, 
        'valor_total': valor_total
    }

    return render(request, 'carrinho.html', context)

@user_passes_test(is_aluno, login_url='usuario_login')
def remover_do_carrinho(request, produto_id):
    """ Diminui a quantidade de um item no pedido aberto ou o remove. """
    # --- IMPLEMENTAÇÃO DO FIXME ---
    pedido_aberto = Pedido.objects.filter(usuario=request.user, status='aberto').first()
    
    if pedido_aberto:
        item_pedido = ItemPedido.objects.filter(pedido=pedido_aberto, produto_id=produto_id).first()
        if item_pedido:
            item_pedido.quantidade -= 1
            if item_pedido.quantidade > 0:
                item_pedido.save()
                messages.info(request, f"Quantidade de '{item_pedido.produto.nome}' atualizada.")
            else:
                # Se a quantidade for 0, o método delete do item já devolve ao estoque
                item_pedido.delete()
                messages.info(request, f"'{item_pedido.produto.nome}' removido do carrinho.")

    # Redireciona para o cardápio para ver a mudança refletida
    return redirect('ver_cardapio')

@user_passes_test(is_aluno, login_url='usuario_login')
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

    context = {
        'valor_total': valor_total_pedido,
        'opcoes_pagamento': Pedido._meta.get_field('pagamento').choices
    }
    return render(request, 'selecionar_pagamento.html', context)

@user_passes_test(is_aluno, login_url='usuario_login')
def confirmar_pedido(request):
    """
    Processa o POST da página de pagamento, cria o pedido e limpa o carrinho.
    """
    if request.method != 'POST':
        # Se não for POST, redireciona para o carrinho, pois não há o que confirmar.
        return redirect('ver_carrinho')

    pedido_aberto = Pedido.objects.filter(usuario=request.user, status='aberto').first()
    if not pedido_aberto or not pedido_aberto.itens.exists():
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('ver_carrinho')

    forma_pagamento = request.POST.get('pagamento', 'dinheiro')

    # Atualiza o pedido existente para o status 'pendente' ou 'preparo'
    # e define a forma de pagamento.
    pedido_aberto.status = 'pendente' # Ou 'preparo', dependendo da sua lógica inicial
    pedido_aberto.pagamento = forma_pagamento
    
    # O valor_total já foi calculado e salvo em finalizar_pedido_carrinho
    # ou pode ser recalculado aqui se preferir.
    # pedido_aberto.valor_total = sum(item.subtotal() for item in pedido_aberto.itens.all())
    
    pedido_aberto.save()

    messages.success(request, "Pedido finalizado com sucesso!")
    return redirect('historico_pedidos')
