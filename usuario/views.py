from django.shortcuts import render, redirect
from .forms import CadastroForm, LoginForm, UsuarioForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from usuario.models import Usuario
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # REMOVER DA PRODUÇÃO - USAR EM DEBUG APENAS
from django.contrib.auth.models import User


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

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                user_obj = Usuario.objects.filter(user__email=email).first()
                if user_obj:
                    user = authenticate(request, username=user_obj.user.username, password=password)
                else:
                    user = None
            except Exception:
                user = None

            if user is not None:
                login(request, user)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': 'Login realizado com sucesso!'})
                return redirect('home')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Email ou senha inválidos'})
                form.add_error(None, 'Email ou senha inválidos.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def gerenciar_pedidos_view(request):
    # lógica para mostrar pedidos
    return render(request, 'gerenciar_pedidos.html')

@login_required
def produtos(request):
    return render(request, 'produtos.html')

@login_required
def fazer_pedido(request):
    return render(request, 'fazer_pedidos')

@login_required
def listar(request):
    return redirect('listar_produtos') 

@login_required
def usuario(request):
    usuario, created = Usuario.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('usuario')
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
    
