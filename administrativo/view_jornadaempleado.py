import datetime
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from baseapp.funciones import add_data_aplication
from baseapp.models import Persona
from core.utils import is_ajax
from core.core import DIAS_SEMANA
from administrativo.models import JornadaLaboral, DetalleJornadaLaboral, JornadaEmpleado, PlantillaPersona
from administrativo.forms import JornadaForm, DetalleJornadaForm, JornadaEmpleadoForm
from authentication.models import CustomUser

def view_jornadaempleado(request):
    global ex
    data = {}
    add_data_aplication(request, data)
    usuario_logeado = request.user
    if Persona.objects.filter(usuario=usuario_logeado, status=True).exists():
        persona_logeado = Persona.objects.get(usuario=usuario_logeado, status=True)
    else:
        persona_logeado = 'SUPERUSUARIO'

    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST['action']

            if action == 'add':
                try:
                    with transaction.atomic():
                        form = JornadaEmpleadoForm(request.POST)
                        if form.is_valid():
                            id_empleado = int(request.POST['empleado'])
                            if id_empleado > 0:
                                jor_emple = JornadaEmpleado.objects.filter(status=True, empleado_id=id_empleado,
                                                                           jornada=form.cleaned_data['jornada'])
                                if not jor_emple.exists():
                                    instance = JornadaEmpleado(
                                        empleado_id=id_empleado,
                                        jornada=form.cleaned_data['jornada'],
                                    )
                                    instance.save(request)
                                    return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                                return JsonResponse(
                                    {'success': False, 'errors': "El empleado ya cuenta con jornada laboral asignada"})
                            return JsonResponse({'success': False, 'errors': "Por favor, seleccione el empleado"})
                        else:
                            return JsonResponse({'success': False, 'errors': form.errors})
                except Exception as e:
                    transaction.set_rollback(True)
                    return JsonResponse({'success': False})

            if action == 'edit':
                try:
                    with transaction.atomic():
                        instance = JornadaEmpleado.objects.get(id=int(request.POST['id']))
                        form = JornadaEmpleadoForm(request.POST)
                        id_empleado = int(request.POST['empleado'])
                        if form.is_valid():
                            if id_empleado > 0:
                                jorna_emple = JornadaEmpleado.objects.filter(status=True,
                                                                             empleado_id=id_empleado).exclude(id=instance.id)
                                if not jorna_emple.exists():
                                    instance.empleado_id = id_empleado
                                    instance.jornada = form.cleaned_data['jornada']
                                    instance.save(request)
                                    return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                                return JsonResponse({'success': False,
                                                     'errors': "El empleado seleccionado ya cuenta con jornada laboral asignada"})
                            return JsonResponse({'success': False, 'errors': "Por favor, seleccione el empleado"})
                        else:
                            return JsonResponse({'success': False, 'errors': form.errors})
                except Exception as e:
                    transaction.set_rollback(True)
                    return JsonResponse({'success': False})

            if action == 'eliminar':
                try:
                    instance = JornadaEmpleado.objects.get(id=int(request.POST['id']))
                    instance.status = False
                    instance.save(request)
                    return JsonResponse({'success': True, 'message': 'Registro eliminado con éxito'})
                except JornadaEmpleado.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'El registro no existe'})

        return JsonResponse({"success": False, "mensaje": "No se ha encontrado success."})
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            if action == 'add':
                try:
                    data['titulo'] = 'Asignar jornada a empleado'
                    data['titulo_formulario'] = 'Formulario de asignación de jornada'
                    data['persona_logeado'] = persona_logeado
                    form = JornadaEmpleadoForm()
                    data['form'] = form
                    return render(request, "jornadaempleado/modal/add.html", data)
                except Exception as ex:
                    pass


            if action == 'edit':
                try:
                    data['titulo'] = 'Editar jornada empleado'
                    data['titulo_formulario'] = 'Formulario de editar jornada empleado'
                    data['action'] = action
                    data['filtro'] = instance = JornadaEmpleado.objects.get(id=int(request.GET['id']))
                    form = JornadaEmpleadoForm(initial={
                        'jornada': instance.jornada,
                        'empleado': instance.empleado,
                    })
                    data['form'] = form
                    data['persona_logeado'] = persona_logeado
                    return render(request, "jornadaempleado/modal/add.html", data)
                except Exception as ex:
                    pass

        else:
            try:
                data['titulo'] = 'Empleados y jornadas'
                data['titulo_tabla'] = 'Empleados y sus jornadas'
                data['persona_logeado'] = persona_logeado
                filtro = (Q(status=True))
                ruta_paginado = request.path
                if 'var' in request.GET:
                    var = request.GET['var']
                    data['var'] = var
                    ruta_paginado += "?var=" + var + "&"
                    search_ = var.strip()
                    ss = search_.split(' ')
                    if len(ss) == 1:
                        filtro = filtro & (Q(empleado__persona__nombres__icontains=search_) |
                                           Q(empleado__persona__apellido1__icontains=search_) |
                                           Q(empleado__persona__apellido2__icontains=search_) |
                                           Q(empleado__persona__cedula__icontains=search_) |
                                           Q(empleado__persona__pasaporte__icontains=search_))
                    else:
                        filtro = filtro & ((Q(empleado__persona__apellido1__icontains=ss[0]) & Q(empleado__persona__apellido2__icontains=ss[1])) |
                                           (Q(empleado__persona__nombres__icontains=ss[0]) & Q(empleado__persona__nombres__icontains=ss[1])))
                lista = JornadaEmpleado.objects.filter(filtro).order_by('id')
                paginator = Paginator(lista, 25)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                data['page_obj'] = page_obj
                return render(request, "jornadaempleado/view.html", data)
            except Exception as ex:
                print('Error on line {}'.format(ex.exc_info()[-1].tb_lineno))

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



