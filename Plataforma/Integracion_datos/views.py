from django.shortcuts import render

def index(request):
    return render(request, 'integracion_datos/index.html', {'message': 'Integración de Datos'})
