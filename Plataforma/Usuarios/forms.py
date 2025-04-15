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

class EditNameForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if Usuario.objects.exclude(id_usuario=self.instance.id_usuario).filter(nombre=nombre).exists():
            raise forms.ValidationError('Este nombre ya está en uso.')
        return nombre

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    confirm_password = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data