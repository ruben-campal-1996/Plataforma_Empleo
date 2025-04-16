from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario

class UsuarioCreationForm(UserCreationForm):
    ROL_CHOICES = [
        ('Administrador', 'Administrador'),
        ('Colaborador', 'Colaborador'),
        ('Gestor de Proyectos', 'Gestor de Proyectos'),
    ]
    
    rol = forms.ChoiceField(choices=ROL_CHOICES, label="Rol del usuario", required=True)

    class Meta:
        model = Usuario
        fields = ('nombre', 'correo', 'telefono', 'password1', 'password2', 'rol')  # Añadimos 'rol'
        labels = {
            'nombre': 'Nombre completo',
            'correo': 'Correo electrónico',
            'telefono': 'Número de teléfono',
        }
        help_texts = {
            'correo': 'Este será el campo para iniciar sesión.',
            'telefono': 'Ejemplo: +1234567890',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']

class UsuarioChangeForm(UserChangeForm):

    class Meta:
        model = Usuario
        fields = ('nombre', 'correo', 'telefono', 'rol', 'is_active', 'is_staff', 'is_superuser')
        labels = {
            'nombre': 'Nombre completo',
            'correo': 'Correo electrónico',
            'telefono': 'Número de teléfono',
            'rol': 'Rol del usuario',
            'is_active': 'Usuario activo',
            'is_staff': 'Acceso al admin',
            'is_superuser': 'Superusuario',
        }



class UserEditForm(forms.ModelForm):
    habilidades = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: electricista, Baja Tensión'}),
        help_text="Introduce palabras clave separadas por comas."
    )
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    telefono = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +34 123 456 789'}),
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'telefono', 'habilidades']

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        print(f"[Form Debug] clean_nombre: nombre recibido='{nombre}', instance.nombre='{self.instance.nombre}'")
        if 'edit_nombre' in self.data and not nombre:
            print("[Form Debug] clean_nombre: Error - Nombre vacío en edit_nombre")
            raise forms.ValidationError("El nombre es obligatorio al editarlo.")
        # Si no se envía nombre, usar el existente o cadena vacía
        result = nombre or self.instance.nombre or ''
        print(f"[Form Debug] clean_nombre: Devolviendo nombre='{result}'")
        return result

    def clean_habilidades(self):
        habilidades_input = self.cleaned_data.get('habilidades', '')
        print(f"[Form Debug] clean_habilidades: habilidades='{habilidades_input}'")
        if habilidades_input:
            return [h.strip() for h in habilidades_input.split(',') if h.strip()]
        return []

class AdminUserEditForm(forms.ModelForm):
    habilidades = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: electricista, Baja Tensión'}),
        help_text="Introduce palabras clave separadas por comas."
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'telefono', 'rol', 'habilidades']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +34 123 456 789'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_habilidades(self):
        habilidades_input = self.cleaned_data.get('habilidades', '')
        if habilidades_input:
            return [h.strip() for h in habilidades_input.split(',') if h.strip()]
        return []

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', 'Las contraseñas no coinciden.')
        return cleaned_data