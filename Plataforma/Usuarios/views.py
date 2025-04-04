# Usuarios/views.py
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UsuarioCreationForm
from .models import Usuario

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
def gestion_usuarios(request):
    usuarios = Usuario.objects.all()
    create_form = UsuarioCreationForm()
    roles = Usuario._meta.get_field('rol').choices

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            form = UsuarioCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.save()
                rol = request.POST.get('rol')
                if rol in dict(roles):
                    usuario = Usuario.objects.get(correo=user.correo)
                    usuario.rol = rol
                    usuario.save()
                messages.success(request, 'Usuario creado exitosamente.')
            else:
                # Mostrar errores específicos del formulario
                messages.error(request, f'Error al crear el usuario: {form.errors.as_text()}')
            return redirect('usuarios:gestion_usuarios')
        
        elif action == 'edit':
            user_id = request.POST.get('user_id')
            usuario = Usuario.objects.get(id_usuario=user_id)
            usuario.nombre = request.POST.get('nombre')
            usuario.correo = request.POST.get('correo')
            usuario.rol = request.POST.get('rol')
            if request.POST.get('password1'):
                usuario.set_password(request.POST.get('password1'))
            usuario.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('usuarios:gestion_usuarios')
        
        elif action == 'delete':
            user_id = request.POST.get('user_id')
            try:
                usuario = Usuario.objects.get(id_usuario=user_id)
                usuario.delete()
                messages.success(request, 'Usuario eliminado exitosamente.')
            except Usuario.DoesNotExist:
                messages.error(request, 'El usuario no existe.')
            return redirect('usuarios:gestion_usuarios')

    return render(request, 'usuarios/gestion_usuarios.html', {
        'usuarios': usuarios,
        'create_form': create_form,
        'roles': roles,
    })