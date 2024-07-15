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
from administrativo.models import JornadaEmpleado, PermisoLaboral
from administrativo.forms import JornadaForm, DetalleJornadaForm, JornadaEmpleadoForm
from authentication.models import CustomUser
from system.seguridad_sistema import control_entrada_modulos, log_auditoria


@login_required
@control_entrada_modulos
@transaction.atomic()
def view_permisoslaborales(request):
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

            if action == 'aprobar':
                try:
                    instance = PermisoLaboral.objects.get(id=int(request.POST['id']))
                    instance.estado = 2
                    instance.save(request)
                    log_auditoria(request, f"Aprueba solicitud permiso laboral: {instance.id}", 2)
                    return JsonResponse({'success': True, 'mensaje': 'Permiso aprobado correctamente!'})
                except JornadaEmpleado.DoesNotExist:
                    return JsonResponse({'success': False, 'mensaje': 'Error al aprobar permiso laboral'})

            if action == 'rechazar':
                try:
                    instance = PermisoLaboral.objects.get(id=int(request.POST['id']))
                    instance.estado = 3
                    instance.save(request)
                    log_auditoria(request, f"Rechaza solicitud permiso laboral: {instance.id}", 2)
                    return JsonResponse({'success': True, 'mensaje': 'Permiso rechazado correctamente!'})
                except JornadaEmpleado.DoesNotExist:
                    return JsonResponse({'success': False, 'mensaje': 'Error al rechazar permiso laboral'})

        return JsonResponse({"success": False, "mensaje": "No se ha encontrado success."})
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

        else:
            try:
                data['titulo'] = 'Permisos laborales'
                data['titulo_tabla'] = 'Permisos laborales'
                data['persona_logeado'] = persona_logeado
                filtro = (Q(status=True) & Q(estado__gt=0))
                ruta_paginado = request.path
                if 'var' in request.GET:
                    var = request.GET['var']
                    data['var'] = var
                    ruta_paginado += "?var=" + var + "&"
                    search_ = var.strip()
                    ss = search_.split(' ')
                    if len(ss) == 1:
                        filtro = filtro & (Q(motivo__icontains=search_))
                    else:
                        filtro = filtro & (Q(motivo__icontains=search_))
                lista = PermisoLaboral.objects.filter(filtro).order_by('id')
                paginator = Paginator(lista, 25)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                data['page_obj'] = page_obj
                return render(request, "permisoslaborales/view.html", data)
            except Exception as ex:
                print('Error on line {}'.format(ex.exc_info()[-1].tb_lineno))



