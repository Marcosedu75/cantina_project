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
        
        # --- REGRA DE NEGÓCIO: Impede que 'Pendente' volte para 'Aberto' ---
        if pedido.status == 'pendente' and novo_status == 'aberto':
            messages.error(request, "Não é possível alterar um pedido 'Pendente' de volta para 'Aberto'.")
            # Redireciona de volta para a mesma página sem fazer a alteração.
            return redirect('atualizar_status', pedido_id=pedido.id)
        # --------------------------------------------------------------------

        # Valida se o status recebido é uma das opções válidas no modelo Pedido
        status_anterior = pedido.status
        opcoes_validas = [choice[0] for choice in Pedido.STATUS_CHOICES]
        if novo_status in opcoes_validas:
            # --- LÓGICA DE ESTOQUE AO ATUALIZAR STATUS ---
            # Devolve o estoque se o pedido for cancelado.
            # A baixa ocorreu quando o pedido foi finalizado (status 'pendente').
            # A devolução só deve acontecer se o pedido estava em 'pendente' ou 'preparo'.
            if novo_status == 'cancelado' and status_anterior in ['pendente', 'preparo']:
                for item in pedido.itens.all():
                    item.produto.estoque += item.quantidade
                    item.produto.save()
                messages.info(request, "Estoque devolvido devido ao cancelamento do pedido.")
            # ----------------------------------------------------
            pedido.status = novo_status
            pedido.save()
            messages.success(request, f"Status do Pedido #{pedido.id} atualizado para '{pedido.get_status_display()}'.")
            return redirect('atualizar_status', pedido_id=pedido.id)

        else:
            messages.error(request, "Status inválido. A atualização falhou.")
            # Redireciona de volta para a página de detalhes ou lista
            return redirect('detalhe_pedido', pedido_id=pedido.id)

    # --- LÓGICA PARA FILTRAR AS OPÇÕES DE STATUS ---
    opcoes_disponiveis = Pedido.STATUS_CHOICES

    # Se o status do pedido já avançou (não é mais 'aberto'),
    # remove a opção 'aberto' da lista para impedir que ele regrida.
    if pedido.status != 'aberto':
        opcoes_disponiveis = [choice for choice in Pedido.STATUS_CHOICES if choice[0] != 'aberto']
    # ------------------------------------------------

    return render(request, 'atualizar_status.html', {'pedido': pedido, 'status_choices': opcoes_disponiveis})
@user_passes_test(is_cantineiro, login_url='usuario_login')
def deletar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        # REGRA: Devolve o estoque se o pedido não foi entregue.
        # O estoque foi debitado nos status 'pendente' e 'preparo'.
        if pedido.status in ['pendente', 'preparo']:
            for item in pedido.itens.all():
                item.produto.estoque += item.quantidade
                item.produto.save()
            messages.success(request, f"Pedido #{pedido.id} excluído e o estoque foi devolvido.")
        
        elif pedido.status in ['entregue', 'cancelado', 'aberto']:
            # Para 'entregue', o estoque não é devolvido.
            # Para 'cancelado', o estoque já foi devolvido na mudança de status.
            # Para 'aberto', o estoque nunca foi debitado.
            pedido.itens.all().delete()
            messages.success(request, f"Pedido #{pedido.id} excluído.")

        # Após tratar os itens, deleta o objeto Pedido.
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
        messages.success(request, f"'{produto.nome}' adicionado ao carrinho.")

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

    # Verifica de qual página o usuário veio para redirecioná-lo corretamente.
    referer_url = request.META.get('HTTP_REFERER')
    # Se a URL de origem contém '/carrinho/', redireciona de volta para o carrinho.
    if referer_url and reverse('ver_carrinho') in referer_url:
        return redirect('ver_carrinho')
    # Caso contrário, o comportamento padrão é redirecionar para o cardápio.
    return redirect('ver_cardapio')

@user_passes_test(is_aluno, login_url='usuario_login')
def finalizar_pedido_carrinho(request):
    """
    Exibe a página de seleção de pagamento com o total do carrinho.
    """
    # Busca o pedido aberto (carrinho) do usuário no banco de dados.
    pedido_aberto = Pedido.objects.filter(usuario=request.user, status='aberto').first()

    # Verifica se o carrinho está vazio (sem pedido aberto ou sem itens).
    if not pedido_aberto or not pedido_aberto.itens.exists():
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('ver_carrinho')

    # Calcula o valor total a partir dos itens no banco de dados.
    valor_total_pedido = sum(item.subtotal() for item in pedido_aberto.itens.all())
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

    # --- VERIFICAÇÃO DE ESTOQUE ANTES DE PROCESSAR ---
    # Percorre todos os itens do carrinho para garantir que há estoque para todos.
    for item in pedido_aberto.itens.all():
        produto = item.produto
        if produto.estoque < item.quantidade:
            messages.error(request, f"Desculpe, o estoque de '{produto.nome}' é insuficiente. Disponível: {produto.estoque}.")
            return redirect('ver_carrinho') # Redireciona de volta ao carrinho

    # --- LÓGICA PARA DAR BAIXA NO ESTOQUE ---
    # O estoque é debitado assim que o pedido é confirmado e se torna 'pendente'.
    for item in pedido_aberto.itens.all():
        produto = item.produto
        produto.estoque -= item.quantidade
        produto.save()

    forma_pagamento = request.POST.get('pagamento', 'dinheiro')

    # Atualiza o pedido existente para o status 'pendente' ou 'preparo'
    # e define a forma de pagamento.
    pedido_aberto.status = 'pendente' # Ou 'preparo', dependendo da sua lógica inicial
    pedido_aberto.pagamento = forma_pagamento
    
    # Calcula e atribui o valor total final ao pedido antes de salvar.
    pedido_aberto.valor_total = sum(item.subtotal() for item in pedido_aberto.itens.all())
    pedido_aberto.save()

    messages.success(request, "Pedido finalizado com sucesso!")
    ultimo_pedido = Pedido.objects.filter(usuario=request.user).order_by('-data_pedido').first()

    return render(request, 'pagamento_concluido.html', {'pedido': ultimo_pedido})
    

@user_passes_test(is_aluno, login_url='usuario_login')
def pagamento_concluido(request):
    """
    Exibe a página de confirmação de pagamento concluído.
    """
    return render(request, 'pagamento_concluido.html')
