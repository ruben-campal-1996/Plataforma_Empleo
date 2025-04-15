# Usuarios/views.py
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UsuarioCreationForm, ChangePasswordForm, EditNameForm
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
def user_details(request):
    user = request.user
    
    if request.method == 'POST' and 'edit_name' in request.POST:
        name_form = EditNameForm(request.POST, instance=user)
        if name_form.is_valid():
            name_form.save()
            messages.success(request, 'Nombre actualizado correctamente.')
            return redirect('usuarios:user_details')
    else:
        name_form = EditNameForm(instance=user)
    
    if request.method == 'POST' and 'change_password' in request.POST:
        password_form = ChangePasswordForm(request.POST)
        if password_form.is_valid():
            current_password = password_form.cleaned_data['current_password']
            new_password = password_form.cleaned_data['new_password']
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Contraseña actualizada correctamente.')
                return redirect('usuarios:user_details')
            else:
                password_form.add_error('current_password', 'Contraseña actual incorrecta.')
    else:
        password_form = ChangePasswordForm()
    
    if request.method == 'POST' and 'delete_account' in request.POST:
        user.delete()
        logout(request)
        messages.success(request, 'Cuenta eliminada correctamente.')
        return redirect('usuarios:login')
    
    context = {
        'name_form': name_form,
        'password_form': password_form,
    }
    return render(request, 'Usuarios/user_details.html', context)


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
                user = form.save()
                messages.success(request, 'Usuario creado exitosamente.')
            else:
                messages.error(request, f'Error al crear el usuario: {form.errors.as_text()}')
            return redirect('usuarios:gestion_usuarios')
        
        elif action == 'edit':
            user_id = request.POST.get('user_id')
            usuario = Usuario.objects.get(id_usuario=user_id)
            if request.POST.get('nombre'):
                usuario.nombre = request.POST.get('nombre')
            if request.POST.get('correo'):
                usuario.correo = request.POST.get('correo')
            if request.POST.get('telefono') is not None:  # Permitir vaciar teléfono
                usuario.telefono = request.POST.get('telefono') or None
            if request.POST.get('rol'):
                usuario.rol = request.POST.get('rol')
            if request.POST.get('password1'):
                usuario.set_password(request.POST.get('password1'))
            usuario.save()
            messages.success(request, 'Usuario actualizado exitosamente.', extra_tags='edit')
            return redirect('usuarios:user_details', id_usuario=user_id)
        
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