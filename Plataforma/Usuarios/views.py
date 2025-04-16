# Usuarios/views.py
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UsuarioCreationForm, ChangePasswordForm, AdminUserEditForm, UserEditForm
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

def admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol != 'Administrador':
            messages.error(request, 'Acceso denegado: se requiere rol de Administrador.')
            return redirect('usuarios:user_details')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def user_details(request):
    user = request.user
    print(f"[View Debug] user_details: user.id={user.id_usuario}, nombre={user.nombre}, correo={user.correo}")
    
    if request.method == 'POST':
        print(f"[View Debug] POST recibido: {request.POST}")
        
        if 'edit_nombre' in request.POST:
            print("[View Debug] Procesando edit_nombre")
            form = UserEditForm(request.POST, instance=user)
            print(f"[View Debug] Formulario inicial: nombre={form.initial.get('nombre')}")
            if form.is_valid():
                old_nombre = user.nombre
                print(f"[View Debug] Formulario válido, old_nombre={old_nombre}")
                form.save()
                user.refresh_from_db()
                new_nombre = user.nombre
                print(f"[View Debug] Nombre guardado, new_nombre={new_nombre}")
                messages.success(request, f'Nombre actualizado correctamente de "{old_nombre}" a "{new_nombre}".')
            else:
                print(f"[View Debug] Formulario inválido, errores={form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Error en {field}: {error}')
        
        elif 'edit_correo' in request.POST:
            print("[View Debug] Procesando edit_correo")
            form = UserEditForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Correo actualizado correctamente.')
            else:
                print(f"[View Debug] Formulario inválido, errores={form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Error en {field}: {error}')
        
        elif 'edit_telefono' in request.POST:
            print("[View Debug] Procesando edit_telefono")
            form = UserEditForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Teléfono actualizado correctamente.')
            else:
                print(f"[View Debug] Formulario inválido, errores={form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Error en {field}: {error}')
        
        elif 'edit_habilidades' in request.POST:
            print("[View Debug] Procesando edit_habilidades")
            form = UserEditForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Habilidades actualizadas correctamente.')
            else:
                print(f"[View Debug] Formulario inválido, errores={form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Error en {field}: {error}')
        
        elif 'change_password' in request.POST:
            print("[View Debug] Procesando change_password")
            password_form = ChangePasswordForm(request.POST)
            if password_form.is_valid():
                current_password = password_form.cleaned_data['current_password']
                new_password = password_form.cleaned_data['new_password']
                if user.check_password(current_password):
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Contraseña actualizada correctamente.')
                else:
                    password_form.add_error('current_password', 'Contraseña actual incorrecta.')
            else:
                print(f"[View Debug] Password form inválido, errores={password_form.errors}")
            form = UserEditForm(instance=user)
        
        elif 'delete_account' in request.POST:
            print("[View Debug] Procesando delete_account")
            user.delete()
            logout(request)
            messages.success(request, 'Cuenta eliminada correctamente.')
            return redirect('usuarios:login')
        
        return redirect('usuarios:user_details')
    else:
        form = UserEditForm(instance=user)
        password_form = ChangePasswordForm()
        print(f"[View Debug] GET request, form.initial.nombre={form.initial.get('nombre')}")

    context = {
        'form': form,
        'password_form': password_form,
        'user': user,
    }
    return render(request, 'Usuarios/user_details.html', context)

@login_required
@admin_required
def gestion_usuarios(request):
    print("[View Debug] gestion_usuarios: Iniciando")
    if request.method == 'POST':
        print(f"[View Debug] gestion_usuarios POST: {request.POST}")
        action = request.POST.get('action')
        if action == 'create':
            form = AdminUserEditForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Usuario creado correctamente.')
            else:
                print(f"[View Debug] gestion_usuarios: Form inválido, errores={form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Error en {field}: {error}')
        else:
            user_id = request.POST.get('user_id')
            if not user_id or not user_id.isdigit():
                messages.error(request, 'ID de usuario inválido.')
                return redirect('usuarios:gestion_usuarios')
            try:
                usuario = Usuario.objects.get(id_usuario=user_id)
                if action == 'delete':
                    usuario.delete()
                    messages.success(request, 'Usuario eliminado correctamente.')
                else:
                    form = AdminUserEditForm(request.POST, instance=usuario)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Usuario actualizado correctamente.')
                    else:
                        print(f"[View Debug] gestion_usuarios: Form inválido, errores={form.errors}")
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f'Error en {field}: {error}')
            except Usuario.DoesNotExist:
                messages.error(request, 'Usuario no encontrado.')
            except Exception as e:
                messages.error(request, f'Error al actualizar: {str(e)}')
        return redirect('usuarios:gestion_usuarios')

    usuarios = Usuario.objects.all()
    context = {
        'usuarios': usuarios,
        'form': AdminUserEditForm(),
    }
    return render(request, 'Usuarios/gestion_usuarios.html', context)