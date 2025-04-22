from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def analisis_view(request):
    context = {
        'active_view': 'analisis',
        'user': request.user,
    }
    return render(request, 'CRUD_escritorio/analisis.html', context)

@login_required
def graficos_view(request):
    context = {
        'active_view': 'graficos',
        'user': request.user,
    }
    return render(request, 'CRUD_escritorio/graficos.html', context)

@login_required
def proyectos_view(request):
    context = {
        'active_view': 'proyectos',
        'user': request.user,
    }
    return render(request, 'CRUD_escritorio/proyectos.html', context)