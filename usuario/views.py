from django.shortcuts import render, redirect
from .forms import CadastroForm, LoginForm, UsuarioForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from usuario.models import Usuario
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # REMOVER DA PRODUÇÃO - USAR EM DEBUG APENAS
from django.contrib.auth.models import User


def home_view(request):
    
    return render(request, 'home.html')

# --- Funções de Teste para Decorators ---

def is_cantineiro(user):
    """Verifica se o usuário é autenticado e tem a role 'cantineiro'."""
    if not user.is_authenticated:
        return False
    return hasattr(user, 'usuario') and user.usuario.role == 'cantineiro'

def is_aluno(user):
    """Verifica se o usuário é autenticado e tem a role 'aluno'."""
    if not user.is_authenticated:
        return False
    return hasattr(user, 'usuario') and user.usuario.role == 'aluno'

@login_required
def login_redirect_view(request):
    usuario = Usuario.objects.filter(user=request.user).first()

    if usuario:
        if usuario.role == 'aluno':
            return redirect('criar_pedidos')  
        elif usuario.role == 'cantineiro':
            return redirect('listar')
    
    return redirect('home') 

@user_passes_test(is_cantineiro, login_url='login')
def dashboard_cantineiro(request):
    usuario = Usuario.objects.filter(user=request.user).first()
    if not usuario or usuario.role != 'cantineiro':
        return redirect('home')
    return render(request, 'dashboard_cantineiro.html', {'usuario': usuario})

#Integração código do Rian
@user_passes_test(is_aluno,login_url='login')
def painel_usuario(request):
    """
    Exibe o painel do usuário. Acessível apenas para usuários logados.
    """
    return render(request, 'painel_usuario.html')

def cadastro_view(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # redireciona para login após cadastro
    else:
        form = CadastroForm()
    return render(request, 'cadastro.html', {'form': form})



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
                return redirect('login_redirect')
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
def perfil(request):
    usuario, created = Usuario.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = UsuarioForm(instance=usuario)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        usuario_data = {
            'foto': usuario.foto.url if usuario.foto else None,
            'username': usuario.user.username,
            'email': usuario.user.email,   
            'nomecompleto: ': usuario.user.get_full_name(),
            'situação': 'Ativo' if usuario.user.is_active else 'Inativo',
            'data_cadastro': usuario.user.date_joined
            
        }
        return JsonResponse({'success': True, 'usuario': usuario_data})

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
    
