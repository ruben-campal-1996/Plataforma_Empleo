import os
import sys
import django
from django.conf import settings
from django.contrib.auth import authenticate
from django.db.models import Count
from django.db.models.functions import TruncDay
from Usuarios.models import Usuario
from CRUD_escritorio.models import ConsultaBusqueda

# Ajustar la ruta para encontrar Plataforma.settings
# Asumiendo que db_connect.py está en Plataforma/CRUD_escritorio/python/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(BASE_DIR)
print(f"BASE_DIR configurado: {BASE_DIR}")
print(f"sys.path: {sys.path}")

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Plataforma.settings')
try:
    django.setup()
    print("Django inicializado correctamente")
except Exception as e:
    print(f"Error inicializando Django: {str(e)}")
    sys.exit(1)

def login_user(username, password):
    print(f"Intentando autenticar: username/email={username}")
    try:
        # Intentar autenticar con email primero
        user = authenticate(email=username, password=password)
        if not user:
            # Si falla, intentar con username
            user = authenticate(username=username, password=password)
        if user:
            print(f"Usuario autenticado: {user}")
            # Obtener campos con valores por defecto
            user_id = getattr(user, 'id_usuario', user.id)
            nombre = getattr(user, 'nombre', user.username or user.email or 'Usuario')
            rol = getattr(user, 'rol', 'desconocido')
            return {
                'id': user_id,
                'nombre': nombre,
                'rol': rol
            }
        else:
            print("Autenticación fallida: credenciales incorrectas")
            return {'error': 'Correo o contraseña incorrectos'}
    except Exception as e:
        print(f"Error en autenticación: {str(e)}")
        return {'error': f'Error en autenticación: {str(e)}'}

def get_analisis_data():
    print("Obteniendo datos de análisis")
    try:
        top_keywords = ConsultaBusqueda.objects.values('palabra_clave').annotate(total=Count('id')).order_by('-total')[:10]
        top_provinces = ConsultaBusqueda.objects.values('provincia').annotate(total=Count('id')).order_by('-total')[:10]
        daily_queries = ConsultaBusqueda.objects.annotate(day=TruncDay('fecha')).values('day').annotate(total=Count('id')).order_by('-day')[:7]
        return {
            'top_keywords': list(top_keywords),
            'top_provinces': list(top_provinces),
            'daily_queries': [{'day': str(item['day']), 'total': item['total']} for item in daily_queries]
        }
    except Exception as e:
        print(f"Error obteniendo datos de análisis: {str(e)}")
        return {}

if __name__ == '__main__':
    import json
    action = sys.argv[1]
    if action == 'login':
        if len(sys.argv) < 4:
            print(json.dumps({'error': 'Faltan argumentos: username y password requeridos'}))
            sys.exit(1)
        username, password = sys.argv[2], sys.argv[3]
        result = login_user(username, password)
        print(json.dumps(result))
    elif action == 'analisis':
        result = get_analisis_data()
        print(json.dumps(result))