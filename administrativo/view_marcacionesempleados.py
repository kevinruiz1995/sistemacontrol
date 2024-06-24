from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.core import meses
from administrativo.models import PlantillaPersona, RegistroEntradaSalidaDiario, MOTIVO_MARCACION
from system.seguridad_sistema import control_entrada_modulos
from baseapp.funciones import add_data_aplication
from baseapp.models import Persona

@login_required
@control_entrada_modulos
@transaction.atomic()
def view_marcacionempleado(request):
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
                    pass
                except Exception as e:
                    transaction.set_rollback(True)
                    return JsonResponse({'success': False})

            if action == 'edit':
                try:
                    pass
                except Exception as e:
                    transaction.set_rollback(True)
                    return JsonResponse({'success': False})

            if action == 'eliminar':
                try:
                    pass
                except Exception as ex:
                    return JsonResponse({'success': False, 'message': 'El registro no existe'})

        return JsonResponse({"success": False, "mensaje": "No se ha encontrado success."})
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

            if action == 'marcacionesempleado':
                try:
                    data['titulo'] = 'Marcaciones del empleado'
                    data['titulo_tabla'] = 'Marcaciones del empleado'
                    data['persona_logeado'] = persona_logeado
                    ruta_paginado = request.path
                    data['empleado'] = empleado = PlantillaPersona.objects.get(id=int(request.GET['id']))
                    filtro = (Q(status=True) & Q(empleado_id=empleado.id))
                    if 'mes' in request.GET:
                        mes = int(request.GET['mes'])
                        ruta_paginado += "?mes_=" + request.GET['mes'] + "&"
                        filtro = filtro & Q(fecha_hora__month=mes)
                    lista = RegistroEntradaSalidaDiario.objects.filter(filtro).order_by('fecha_hora__day')
                    paginator = Paginator(lista, 25)
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                    data['page_obj'] = page_obj
                    data['MOTIVO_MARCACION'] = MOTIVO_MARCACION
                    data['meses'] = meses
                    return render(request, "marcacionesempleado/viewdetalle.html", data)
                except Exception as ex:
                    print('Error on line {}'.format(ex.exc_info()[-1].tb_lineno))

        else:
            try:
                data['titulo'] = 'Empleados y sus marcadas'
                data['titulo_tabla'] = 'Empleados y sus marcadas'
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
                        filtro = filtro & (Q(persona__nombres__icontains=search_) |
                                           Q(persona__apellido1__icontains=search_) |
                                           Q(persona__apellido2__icontains=search_) |
                                           Q(persona__cedula__icontains=search_) |
                                           Q(persona__pasaporte__icontains=search_))
                    else:
                        filtro = filtro & ((Q(persona__apellido1__icontains=ss[0]) & Q(persona__apellido2__icontains=ss[1])) |
                    (Q(persona__nombres__icontains=ss[0]) & Q(persona__nombres__icontains=ss[1])))
                lista = PlantillaPersona.objects.filter(filtro).order_by('id')
                paginator = Paginator(lista, 25)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                data['page_obj'] = page_obj
                return render(request, "marcacionesempleado/view.html", data)
            except Exception as ex:
                print('Error on line {}'.format(ex.exc_info()[-1].tb_lineno))

@login_required
@control_entrada_modulos
@transaction.atomic()
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
