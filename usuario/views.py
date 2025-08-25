from django.shortcuts import render, redirect
from .forms import CadastroForm, LoginForm
from django.contrib.auth import authenticate, login, logout


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
    if request.user.tipo_usuario == 'aluno':
        return redirect('dashboard_aluno')
    elif request.user.tipo_usuario == 'cantineiro':
        return redirect('dashboard_cantineiro')
    else:
        return redirect('/')






