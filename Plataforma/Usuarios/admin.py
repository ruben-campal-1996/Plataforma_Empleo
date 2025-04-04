from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class CustomUserAdmin(UserAdmin):
    # Campos que se muestran en la lista de usuarios
    list_display = ('nombre', 'correo', 'telefono', 'rol', 'is_staff')
    # Campos que se pueden buscar
    search_fields = ('nombre', 'correo', 'telefono')
    # Campos que aparecen en el formulario de edición
    fieldsets = (
        (None, {'fields': ('nombre', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email', 'telefono')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Rol', {'fields': ('rol',)}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    # Campos para añadir un nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nombre', 'correo', 'telefono', 'rol', 'password1', 'password2'),
        }),
    )

# Registrar el modelo con el admin personalizado
admin.site.register(Usuario, CustomUserAdmin)