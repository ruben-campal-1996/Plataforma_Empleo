from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

class CustomUserManager(UserManager):
    def _create_user(self, correo, password, **extra_fields):
        if not correo:
            raise ValueError('El campo correo es obligatorio')
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(correo, password, **extra_fields)

    def create_superuser(self, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'Administrador')  # Rol por defecto para superusuario
        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True')
        return self._create_user(correo, password, **extra_fields)

class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('Administrador', 'Administrador'),
        ('Gestor de Proyectos', 'Gestor de Proyectos'),
        ('Colaborador', 'Colaborador'),
    ]
    
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, unique=True)
    correo = models.EmailField(max_length=200, unique=True)
    telefono = models.CharField(max_length=15, unique=True, blank=True, null=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='Colaborador')
    # Campo username requerido por Django, pero opcional en nuestro caso
    username = models.CharField(max_length=150, unique=False, blank=True, null=True, default=None)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'correo'  # Usamos correo como identificador principal
    REQUIRED_FIELDS = ['nombre']  # Campos obligatorios al crear un usuario

    def __str__(self):
        return self.nombre
