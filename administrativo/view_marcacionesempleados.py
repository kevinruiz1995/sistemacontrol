from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.core import meses
from administrativo.models import PlantillaPersona, RegistroEntradaSalidaDiario, MOTIVO_MARCACION


@login_required
def listar_personasmarcaciones(request,search=None):
    try:
        parametros = ''
        personal = PlantillaPersona.objects.filter(status=True)
        if 'search' in request.GET:
            search_ = search = request.GET['search']
            parametros += '&search=' + search_
            search_ = search_.strip()
            ss = search_.split(' ')
            if len(ss) == 1:
                personal = personal.filter(Q(persona__nombres__icontains=search) |
                                           Q(persona__apellido1__icontains=search) |
                                           Q(persona__apellido2__icontains=search) |
                                           Q(persona__cedula__icontains=search) |
                                           Q(persona__pasaporte__icontains=search))
            else:
                personal = personal.filter(
                    (Q(persona__apellido1__icontains=ss[0]) & Q(persona__apellido2__icontains=ss[1])) |
                    (Q(persona__nombres__icontains=ss[0]) & Q(persona__nombres__icontains=ss[1])))

        paginator = Paginator(personal, 25)
        page = request.GET.get('page')
        try:
            page_object = paginator.page(page)
        except PageNotAnInteger:
            page_object = paginator.page(1)
        except EmptyPage:
            page_object = paginator.page(paginator.num_pages)

        context = {
            'page_object': page_object,
            'page_titulo': "Empleados y sus marcadas",
            'titulo': "Empleados y sus marcadas",
            'search': search,
            'parametros': parametros,
        }
        return render(request, 'marcacionesempleado/inicio.html', context)
    except Exception as e:
        HttpResponseRedirect(f"/?info={e.__str__()}")

@login_required
def listar_marcacionesempleado(request, id,search=None):
    try:
        marcaciones, mes, parametros = [], None, ''
        mes = None
        empleado = PlantillaPersona.objects.get(id=int(id))
        if 'mes' in request.GET:
            mes = int(request.GET['mes'])
            parametros += '&mes=' + str(mes)
            marcaciones = RegistroEntradaSalidaDiario.objects.filter(status=True, empleado_id=id, fecha_hora__month=mes).order_by('fecha_hora__day')
        paginator = Paginator(marcaciones, 25)
        page = request.GET.get('page')
        try:
            page_object = paginator.page(page)
        except PageNotAnInteger:
            page_object = paginator.page(1)
        except EmptyPage:
            page_object = paginator.page(paginator.num_pages)

        context = {
            'page_object': page_object,
            'page_titulo': "Marcaciones del empleado",
            'titulo': "Marcaciones del empleado",
            'MOTIVO_MARCACION': MOTIVO_MARCACION,
            'meses': meses,
            'mes_': mes,
            'parametros': parametros,
            'subobjeto': empleado,
        }
        return render(request, 'marcacionesempleado/detallemarcadas.html', context)
    except Exception as e:
        HttpResponseRedirect(f"/?info={e.__str__()}")
