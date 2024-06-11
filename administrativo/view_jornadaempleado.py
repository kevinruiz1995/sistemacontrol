import datetime
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.utils import is_ajax
from core.core import DIAS_SEMANA
from administrativo.models import JornadaLaboral, DetalleJornadaLaboral, JornadaEmpleado, PlantillaPersona
from administrativo.forms import JornadaForm, DetalleJornadaForm, JornadaEmpleadoForm
from authentication.models import CustomUser


@login_required
def listar_jornadaempleado(request,search=None):
    try:
        parametros = ''
        jornadaempleado = JornadaEmpleado.objects.filter(status=True)
        if 'search' in request.GET:
            search_ = search = request.GET['search']
            parametros += '&search=' + search_
            search_ = search_.strip()
            ss = search_.split(' ')
            if len(ss) == 1:
                jornadaempleado = jornadaempleado.filter(Q(empleado__persona__nombres__icontains=search) |
                                           Q(empleado__persona__apellido1__icontains=search) |
                                           Q(empleado__persona__apellido2__icontains=search) |
                                           Q(empleado__persona__cedula__icontains=search) |
                                           Q(empleado__persona__pasaporte__icontains=search))
            else:
                jornadaempleado = jornadaempleado.filter((Q(empleado__persona__apellido1__icontains=ss[0]) & Q(empleado__persona__apellido2__icontains=ss[1])) |
                                           (Q(empleado__persona__nombres__icontains=ss[0]) & Q(empleado__persona__nombres__icontains=ss[1])))

        paginator = Paginator(jornadaempleado, 25)
        page = request.GET.get('page')
        try:
            page_object = paginator.page(page)
        except PageNotAnInteger:
            page_object = paginator.page(1)
        except EmptyPage:
            page_object = paginator.page(paginator.num_pages)

        context = {
            'page_object': page_object,
            'page_titulo': "Empleados y jornadas",
            'titulo': "Empleados y sus jornadas",
            'DIAS_SEMANA': DIAS_SEMANA,
            'search': search,
            'parametros': parametros,
        }
        return render(request, 'jornadaempleado/inicio.html', context)
    except Exception as e:
        HttpResponseRedirect(f"/?info={e.__str__()}")

@login_required
def crear_jornadaempleado(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = JornadaEmpleadoForm(request.POST)
                if form.is_valid():
                    id_empleado = int(request.POST['id_empleado'])
                    if id_empleado > 0:
                        jor_emple = JornadaEmpleado.objects.filter(status=True, empleado_id=id_empleado, jornada=form.cleaned_data['jornada'])
                        if not jor_emple.exists():
                            instance = JornadaEmpleado(
                                empleado_id=int(request.POST['id_empleado']),
                                jornada=form.cleaned_data['jornada'],
                            )
                            instance.save(request)
                            return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                        return JsonResponse({'success': False, 'errors': "El empleado ya cuenta con jornada laboral asignada"})
                    return JsonResponse({'success': False, 'errors': "Por favor, seleccione el empleado"})
                else:
                    return JsonResponse({'success': False, 'errors': form.errors})
        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'success': False})
    else:
        if is_ajax(request):
            form = JornadaEmpleadoForm()
        else:
            return redirect('administrativo:listar_jornadaempleado')
    context = {
        'form': form,
    }
    return render(request, 'jornadaempleado/modales/formulario.html', context)

@login_required
def editar_jornadaempleado(request, pk):
    instance = get_object_or_404(JornadaEmpleado, pk=pk)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = JornadaEmpleadoForm(request.POST, instance=instance)
                id_empleado = int(request.POST['id_empleado'])
                if form.is_valid():
                    if id_empleado > 0:
                        jorna_emple = JornadaEmpleado.objects.filter(status=True, empleado_id=id_empleado).exclude(id=pk)
                        if not jorna_emple.exists():
                            instance.empleado_id = id_empleado
                            instance.jornada = form.cleaned_data['jornada']
                            instance.save(request)
                            return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                        return JsonResponse({'success': False, 'errors': "El empleado seleccionado ya cuenta con jornada laboral asignada"})
                    return JsonResponse({'success': False, 'errors': "Por favor, seleccione el empleado"})
                else:
                    return JsonResponse({'success': False, 'errors': form.errors})
        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'success': False})
    else:
        if is_ajax(request):
            form = JornadaEmpleadoForm(initial={
                'jornada': instance.jornada,
            })
        else:
            return redirect('administrativo:listar_jornadaempleado')
    context = {
        'form': form,
        'instance': instance,
    }
    return render(request, 'jornadaempleado/modales/edit.html', context)
@login_required
def eliminar_jornadaempleado(request, pk):
    try:
        instance = get_object_or_404(JornadaEmpleado, pk=pk)
        if request.method == 'POST':
            instance.eliminar_registro(request)
            return JsonResponse({'success': True, 'message': 'Registro eliminado con éxito'})
    except JornadaEmpleado.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'El registro no existe'})

@login_required
def consultarempleados(request):
    try:
        # Obtiene el término de búsqueda desde la solicitud GET
        search_term = request.GET.get('q', '').strip()
        resultados = PlantillaPersona.objects.filter(status=True)

        # Realiza la búsqueda en la base de datos (este es un ejemplo simple, adapta según tu modelo)
        ss = search_term.split(' ')
        if len(ss) == 1:
            resultados = resultados.filter(Q(persona__nombres__icontains=search_term) |
                                                       Q(persona__apellido1__icontains=search_term) |
                                                       Q(persona__apellido2__icontains=search_term) |
                                                       Q(persona__cedula__icontains=search_term) |
                                                       Q(persona__pasaporte__icontains=search_term))
        else:
            resultados = resultados.filter(Q(persona__nombres__icontains=search_term) |
                                           (Q(persona__apellido1__icontains=ss[0]) | Q(persona__apellido2__icontains=ss[1])))

        # Obtén los nombres de las personas como lista
        resultados = [{'id': persona.id, 'nombre': persona.persona.__str__(), 'cedula': persona.persona.get_card_id()} for persona in resultados[:5]]

        # Devuelve los resultados en formato JSON
        return JsonResponse(resultados, safe=False)
    except Exception as ex:
        return JsonResponse([], safe=False)



