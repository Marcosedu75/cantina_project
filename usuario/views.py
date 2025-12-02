from django.shortcuts import render, redirect
from .forms import CadastroForm, LoginForm, UsuarioForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # REMOVER DA PRODUÇÃO - USAR EM DEBUG APENAS
from django.contrib.auth.models import User
from django.contrib import messages
from usuario.models import Usuario
from pedido.models import Pedido

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
            return redirect('ver_cardapio')  
        elif usuario.role == 'cantineiro':
            return redirect('listar')
    
    return redirect('home') 

@user_passes_test(is_cantineiro, login_url='usuario_login')
def dashboard_cantineiro(request):
    usuario = Usuario.objects.filter(user=request.user).first()
    if not usuario or usuario.role != 'cantineiro':
        return redirect('home')
    return render(request, 'dashboard_cantineiro.html', {'usuario': usuario})

#Integração código do Rian
@user_passes_test(is_aluno,login_url='usuario_login')
def painel_usuario(request):
    """
    Exibe o painel do usuário. Acessível apenas para usuários logados.
    """
    return render(request, 'painel_usuario.html')

def cadastro_view(request):
    if request.method == 'POST':
        # Coleta dos dados do formulário manual
        # O campo 'nome' do HTML será o 'username' no Django
        username = request.POST.get('username') 
        email = request.POST.get('email')
        password = request.POST.get('password')

        # --- Validações Manuais ---
        if not all([username, email, password]):
            messages.error(request, 'Todos os campos são obrigatórios.')
            return redirect('cadastro_view')

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.error(request, 'Não foi possível realizar o cadastro. Verifique os dados e tente novamente.')
            return redirect('cadastro_view')

        # --- Criação do Usuário ---
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Salva o username também como o primeiro nome para exibição
        user.first_name = username
        user.save()

        # Cria o perfil de usuário associado
        Usuario.objects.create(user=user, role='aluno')

        messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')
        return redirect('usuario_login')

    return render(request, 'cadastro.html')



@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        # form = LoginForm(request.POST)
        # if form.is_valid():
        # email = form.cleaned_data['email']
        # password = form.cleaned_data['password']
        email = request.POST.get('email')
        password = request.POST.get('password')
        
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
            messages.success(request, 'Login realizado com sucesso!')
            
            # --- IMPLEMENTAÇÃO DO TODO ---
            # Garante que um pedido com status 'aberto' seja criado/obtido
            # apenas para usuários com a role de 'aluno'.
            if hasattr(request.user, 'usuario') and request.user.usuario.role == 'aluno':
                pedido, created = Pedido.objects.get_or_create(
                    usuario=request.user,
                    status='aberto'
                )
            return redirect('login_redirect')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Email ou senha inválidos'})
            # form.add_error(None, 'Email ou senha inválidos.')
        # form = LoginForm()
            messages.error(request, "Dados inválidos. Realize o login novamente.")
            return render(request, 'login.html')

    return render(request, 'login.html')    


def logout_view(request):
    logout(request)
    return redirect('usuario_login')




@login_required
def perfil(request):
    usuario, created = Usuario.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Verifica se a remoção da foto foi solicitada
        if request.POST.get('remover_foto'):
            # Deleta o arquivo de imagem do armazenamento
            usuario.foto.delete(save=False) 
            # Remove a referência da foto no banco de dados
            usuario.foto = None 
            messages.success(request, "Foto do perfil removida com sucesso!")

        # Verifica se uma nova foto foi enviada (pode acontecer na mesma requisição)
        if 'foto' in request.FILES:
            usuario.foto = request.FILES['foto']
            messages.success(request, "Foto do perfil atualizada com sucesso!")
        
        # Salva todas as alterações (remoção e/ou upload) de uma vez
        usuario.save()

        return redirect('perfil')

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

    return render(request, 'perfil.html', {'usuario': usuario})

@login_required
def deletar_conta(request):
    if request.method == 'POST':
        user = request.user

        # --- LÓGICA DE ESTOQUE AO EXCLUIR CONTA ---
        # Itera sobre todos os pedidos do usuário para tratar o estoque.
        pedidos_do_usuario = Pedido.objects.filter(usuario=user)
        for pedido in pedidos_do_usuario:
            # Devolve o estoque para pedidos que não foram entregues ou cancelados.
            # O estoque foi debitado nos status 'pendente' e 'preparo'.
            if pedido.status in ['pendente', 'preparo']:
                for item in pedido.itens.all():
                    item.produto.estoque += item.quantidade
                    item.produto.save()
        # ----------------------------------------------------

        logout(request)  # Faz o logout antes de deletar para invalidar a sessão
        user.delete() # Deletar o usuário também deletará seus pedidos em cascata
        messages.success(request, 'Sua conta foi excluída com sucesso.')
        return redirect('home')  # Redireciona para a página inicial

    # Se o método for GET, apenas renderiza a página de confirmação
    return render(request, 'contadelete.html')
    
