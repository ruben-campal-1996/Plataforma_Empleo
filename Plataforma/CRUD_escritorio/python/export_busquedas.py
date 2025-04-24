import os
import sys
import json
import django
from datetime import datetime
from django.db.models.functions import TruncMonth

# Configurar las rutas para Django
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'Usuarios'))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Plataforma.settings')
django.setup()

from CRUD_escritorio.models import ConsultaBusqueda

def export_busquedas_for_month(year, month):
    # Directorio donde se guardarán los archivos
    output_dir = os.path.join(BASE_DIR, 'CRUD_escritorio', 'data', 'busquedas')
    os.makedirs(output_dir, exist_ok=True)

    # Nombre del archivo basado en el año y mes
    filename = f"busquedas_{year}_{month:02d}.json"
    filepath = os.path.join(output_dir, filename)

    # Filtrar las búsquedas del mes especificado
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    busquedas = ConsultaBusqueda.objects.filter(
        fecha__gte=start_date,
        fecha__lt=end_date
    ).values('palabra_clave', 'provincia', 'fecha')

    # Convertir a lista y guardar en JSON
    busquedas_list = list(busquedas)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(busquedas_list, f, default=str, ensure_ascii=False, indent=2)

    print(f"Exportado {len(busquedas_list)} búsquedas a {filepath}")

    # Opcional: Eliminar los registros de la base de datos después de exportar
    # busquedas.delete()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python export_busquedas.py <año> <mes>")
        sys.exit(1)

    try:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        export_busquedas_for_month(year, month)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)