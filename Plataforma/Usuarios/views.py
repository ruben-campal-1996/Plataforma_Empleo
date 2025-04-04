# Usuarios/views.py
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UsuarioCreationForm

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.rol == 'Administrador'

def index(request):
    return render(request, 'usuarios/index.html')

def register_view(request):
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.rol = 'Colaborador'
            user.save()
            messages.success(request, 'Cuenta creada. ¡Inicia sesión!')
            return redirect('usuarios:login')  # /index/login/
        messages.error(request, 'Error en el formulario.')
    else:
        form = UsuarioCreationForm()
    return render(request, 'usuarios/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        if not username_or_email or not password:
            messages.error(request, "Ingresa ambos campos.")
            return redirect('usuarios:login')  # /index/login/
        user = authenticate(request, username=username_or_email, password=password)
        if not user and '@' in username_or_email:
            try:
                user_obj = User.objects.get(correo=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        if user:
            login(request, user)
            return redirect('usuarios:index')  # /index/
        messages.error(request, "Credenciales incorrectas.")
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    return redirect('usuarios:index')  # /index/

@login_required
@user_passes_test(is_admin)
def gestion_usuarios(request):
    usuarios = User.objects.all()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            form = UsuarioCreationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Usuario creado.')
            else:
                messages.error(request, 'Error al crear.')
        elif action == 'delete':
            user_id = request.POST.get('user_id')
            User.objects.get(id=user_id).delete()
            messages.success(request, 'Usuario eliminado.')
        else:
            messages.error(request, 'Acción no válida.')
        return redirect('usuarios:gestion_usuarios')  # /index/gestion_usuarios/
    form = UsuarioCreationForm()
    return render(request, 'usuarios/gestion_usuarios.html', {'usuarios': usuarios, 'form': form})