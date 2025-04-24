import os
import sys
import django
from django.conf import settings
from django.contrib.auth import authenticate
import json

# Ajustar la ruta al directorio raíz del proyecto Django (Plataforma)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'Usuarios'))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Plataforma.settings')
try:
    django.setup()
    from Usuarios.models import Usuario
except Exception as e:
    print(json.dumps({'error': f'Error inicializando Django: {str(e)}'}))
    sys.exit(1)

def login_user(correo, password):
    try:
        # Autenticar usando el campo correo
        user = authenticate(correo=correo, password=password)
        if user:
            return {
                'id': user.id_usuario,
                'nombre': user.nombre,
                'rol': user.rol
            }
        else:
            return {'error': 'Correo o contraseña incorrectos'}
    except Exception as e:
        return {'error': f'Error en autenticación: {str(e)}'}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Faltan argumentos'}))
        sys.exit(1)

    action = sys.argv[1]
    if action == 'login':
        if len(sys.argv) < 4:
            print(json.dumps({'error': 'Faltan argumentos: correo y password requeridos'}))
            sys.exit(1)
        correo, password = sys.argv[2], sys.argv[3]
        result = login_user(correo, password)
        print(json.dumps(result))
    else:
        print(json.dumps({'error': 'Acción no reconocida'}))