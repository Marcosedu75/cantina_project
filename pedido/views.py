from django.shortcuts import render, get_object_or_404, redirect
from .models import Pedido, ItemPedido, Produto
from usuario.models import Usuario
from django.contrib.auth.decorators import login_required
from .forms import AtualizarStatusForm

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

@login_required
def listar_pedidos(request):
    usuario = get_object_or_404(Usuario, user=request.user)
    if usuario.role != 'cantineiro':
        return redirect('home')
    pedidos = Pedido.objects.prefetch_related('usuario').order_by('-data_pedido')
    #pedidos = DUMMY_PEDIDOS.values()  # Usar .values() para iterar sobre os valores do dicionário
    return render(request, 'listar.html', {'pedidos': pedidos})

@login_required
def detalhe_pedido(request, pedido_id):
    usuario = get_object_or_404(Usuario, user=request.user)
    if usuario.role != 'cantineiro':
        return redirect('home')
    pedido = get_object_or_404(Pedido, id=pedido_id)
    itens = pedido.itens.select_related('produto')
    return render(request, 'detalhe.html', {'pedido': pedido, 'itens': itens})

@login_required
def atualizar_status(request, pedido_id):
    usuario = get_object_or_404(Usuario, user=request.user)
    if usuario.role != 'cantineiro':
        return redirect('home')
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        form = AtualizarStatusForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            return redirect('listar')
    else:
        form = AtualizarStatusForm(instance=pedido)
    return render(request, 'atualizar_status.html', {'form': form, 'pedido': pedido})

@login_required
def deletar_pedido(request, pedido_id):
    usuario = get_object_or_404(Usuario, user=request.user)
    if usuario.role != 'cantineiro':
        return redirect('home')
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


@login_required(login_url='login')
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

@login_required(login_url='login')
def historico_pedidos(request):
    # Busca os pedidos do usuário logado, do mais recente para o mais antigo
    pedidos_do_usuario = Pedido.objects.filter(usuario=request.user).order_by('-data_pedido')
    context = {'pedidos': pedidos_do_usuario}
    return render(request, 'historico_pedidos.html', context)