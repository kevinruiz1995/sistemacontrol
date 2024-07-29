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
from administrativo.forms import PermisoLaboralForm
from authentication.models import CustomUser
from system.seguridad_sistema import control_entrada_modulos, log_auditoria


@login_required
@control_entrada_modulos
@transaction.atomic()
def view_mispermisoslaborales(request):
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
                        form = PermisoLaboralForm(request.POST)
                        if form.is_valid():
                            permiso = PermisoLaboral.objects.filter(status=True, persona=persona_logeado, motivo__icontains=form.cleaned_data['motivo'])
                            if not permiso.exists():
                                instance = PermisoLaboral(
                                    persona=persona_logeado,
                                    motivo=form.cleaned_data['motivo'],
                                    fecha_inicio=form.cleaned_data['fecha_inicio']
                                )
                                instance.save(request)
                                if 'archivo' in request.FILES:
                                    archivo = request.FILES['archivo']
                                    extension = archivo._name[archivo._name.rfind("."):]
                                    archivo._name = "evidenciapermiso_" + str(instance.id) + '_' + str(datetime.now()).replace('-', '_') + extension.lower()
                                    instance.archivo = archivo
                                    instance.save(request)
                                else:
                                    return JsonResponse({'success': False, 'mensaje': 'Por favor, elija un archivo'})
                                log_auditoria(request, f"Adiciona solicitud permiso laboral: {instance.id}", 1)
                                return JsonResponse({'success': True, 'mensaje': 'Acción realizada con éxito!'})
                            else:
                                return JsonResponse({'success': False, 'mensaje': "Solicitud de permiso laboral ya se encuentra registrado con el mismo motivo."})
                        else:
                            return JsonResponse({'success': False, 'mensaje': form.errors})
                except Exception as e:
                    transaction.set_rollback(True)
                    return JsonResponse({'success': False})

            if action == 'edit':
                try:
                    with transaction.atomic():
                        instance = PermisoLaboral.objects.get(id=int(request.POST['id']))
                        form = PermisoLaboralForm(request.POST)
                        if form.is_valid():
                            permiso = PermisoLaboral.objects.filter(status=True, persona=persona_logeado, motivo__icontains=form.cleaned_data['motivo']).exclude(id=instance.id)
                            if not permiso.exists():
                                instance.motivo = form.cleaned_data['motivo']
                                instance.fecha_inicio = form.cleaned_data['fecha_inicio']
                                instance.save(request)
                                if 'archivo' in request.FILES:
                                    archivo = request.FILES['archivo']
                                    extension = archivo._name[archivo._name.rfind("."):]
                                    archivo._name = "evidenciapermiso_" + str(instance.id) + '_' + str(datetime.now()).replace('-', '_') + extension.lower()
                                    instance.archivo = archivo
                                    instance.save(request)
                                else:
                                    return JsonResponse({'success': False, 'mensaje': 'Por favor, elija un archivo'})
                                log_auditoria(request, f"Edita solicitud permiso laboral: {instance.id}", 2)
                                return JsonResponse({'success': True, 'mensaje': 'Acción realizada con éxito!'})
                            else:
                                return JsonResponse({'success': False, 'mensaje': "Solicitud de permiso laboral ya se encuentra registrado con el mismo motivo."})
                        else:
                            return JsonResponse({'success': False, 'mensaje': form.errors})
                except Exception as e:
                    transaction.set_rollback(True)
                    return JsonResponse({'success': False})

            if action == 'eliminar':
                try:
                    instance = PermisoLaboral.objects.get(id=int(request.POST['id']))
                    instance.status = False
                    instance.save(request)
                    log_auditoria(request, f"Elimina solicitud permiso laboral: {instance.id}", 3)
                    return JsonResponse({'success': True, 'mensaje': 'Registro eliminado con éxito'})
                except JornadaEmpleado.DoesNotExist:
                    return JsonResponse({'success': False, 'mensaje': 'El registro no existe'})

        return JsonResponse({"success": False, "mensaje": "No se ha encontrado success."})
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            if action == 'add':
                try:
                    data['titulo'] = 'Solicitud de justificación de faltas'
                    data['titulo_formulario'] = 'Formulario de justificación de faltas'
                    data['persona_logeado'] = persona_logeado
                    form = PermisoLaboralForm()
                    data['form'] = form
                    return render(request, "mispermisoslaborales/modal/add.html", data)
                except Exception as ex:
                    pass


            if action == 'edit':
                try:
                    data['titulo'] = 'Editar justificación laboral'
                    data['titulo_formulario'] = 'Formulario de editar justificación laboral'
                    data['action'] = action
                    data['filtro'] = instance = PermisoLaboral.objects.get(id=int(request.GET['id']))
                    form = PermisoLaboralForm(initial={
                        'motivo': instance.motivo,
                        'fecha_inicio': instance.fecha_inicio,
                        'archivo': instance.archivo,
                    })
                    data['form'] = form
                    data['persona_logeado'] = persona_logeado
                    return render(request, "mispermisoslaborales/modal/add.html", data)
                except Exception as ex:
                    pass

        else:
            try:
                data['titulo'] = 'Mis justificaciones laborales'
                data['titulo_tabla'] = 'Mis justificaciones laborales'
                data['persona_logeado'] = persona_logeado
                filtro = (Q(status=True) & Q(persona=persona_logeado))
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
                return render(request, "mispermisoslaborales/view.html", data)
            except Exception as ex:
                print('Error on line {}'.format(ex.exc_info()[-1].tb_lineno))



