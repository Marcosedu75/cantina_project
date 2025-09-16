from django.shortcuts import render, get_object_or_404, redirect
from .models import Pedido, ItemPedido
from usuario.models import Usuario
from django.contrib.auth.decorators import login_required
from .forms import AtualizarStatusForm

@login_required
def listar(request):
    usuario = get_object_or_404(Usuario, user=request.user)
    if usuario.role != 'cantineiro':
        return redirect('home')
    pedidos = Pedido.objects.prefetch_related('itens__produto', 'usuario').order_by('-data_pedido')
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
            return redirect('listar_pedidos')
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
        pedido.delete()
        return redirect('listar_pedidos')
    return render(request, 'delete.html', {'pedido': pedido})

    #aluno


def listar_pedidos(request):
    return render(request, 'listar_pedidos.html')

def criar_pedidos(request):
    return render(request, 'criar_pedidos.html')

def historico_pedidos(request):
    return render(request, 'historico_pedidos.html')