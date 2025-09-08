from django.shortcuts import render, redirect
from .forms import CadastroForm, LoginForm, UsuarioForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Usuario



def home_view(request):
    return render(request, 'home.html')


def cadastro_view(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # redireciona para login após cadastro
    else:
        form = CadastroForm()
    return render(request, 'cadastro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                return redirect('home')  # ou redirecionar por tipo de perfil
            else:
                form.add_error(None, 'Usuário ou senha inválidos.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('login')

def login_redirect_view(request):
    if request.user.perfil.role == 'aluno':
        return render(request, 'dashboard_aluno.html')
    if request.user.perfil.role == 'cantineiro':
        return render(request, 'dashboard_cantineiro.html')
    return redirect('home')

def gerenciar_pedidos_view(request):
    # lógica para mostrar pedidos
    return render(request, 'gerenciar_pedidos.html')

def produtos(request):
    return render(request, 'produtos.html')

def fazer_pedido(request):
    return render(request, 'fazer_pedidos')

def listar(request):
    return redirect('listar_produtos') 

@login_required
def perfil_usuario(request):
    usuario, created = Usuario.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('perfil_usuario')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'perfil.html', {'form': form, 'usuario': usuario})

@login_required
def deletar_conta(request):
    if request.method == "POST":
        confirm_text = request.POST.get("confirm_text", "").strip()
        if confirm_text == "delete":
            user = request.user
            logout(request)
            user.delete()
            return redirect("home")
        else:
            # Retorna para a página de confirmação com erro
            return render(request, "contadelete.html", {
                "erro": "Você precisa digitar 'delete' para confirmar."
            })

    return render(request, "contadelete.html")
    
