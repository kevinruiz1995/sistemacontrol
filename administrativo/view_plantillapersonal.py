from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.utils import is_ajax
from baseapp.funciones import add_data_aplication
from baseapp.models import Persona
from administrativo.forms import PlantillaPersonalForm
from administrativo.models import PlantillaPersona, PersonaPerfil

def view_personal(request):
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
                        form = PlantillaPersonalForm(request.POST)
                        if form.is_valid():
                            instance = PlantillaPersona(
                                persona=form.cleaned_data['persona'],
                                cargo=form.cleaned_data['cargo'],
                                coordenadamarcacion=form.cleaned_data['coordenadamarcacion'],
                                salario=form.cleaned_data['salario'],
                                fecha_ingreso=form.cleaned_data['fecha_ingreso'],
                                fecha_terminacion=form.cleaned_data['fecha_terminacion'],
                                area=form.cleaned_data['area'],
                                activo=form.cleaned_data['activo'],
                            )
                            instance.save(request)
                            perfil_persona = PersonaPerfil.objects.filter(status=True,
                                                                          persona=form.cleaned_data['persona'])
                            if perfil_persona.exists():
                                perfil_persona = perfil_persona.first()
                                perfil_persona.is_empleado = True
                                perfil_persona.save(request)
                            else:
                                perfil_persona = PersonaPerfil(persona=form.cleaned_data['persona'],
                                                              is_empleado=True)
                                perfil_persona.save(request)
                            return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                        else:
                            return JsonResponse({'success': False, 'errors': form.errors})
                except Exception as e:
                    transaction.set_rollback(True)
                    return JsonResponse({"success": False, "mensaje": "Ha ocurrido un error, intente más tarde."})

            if action == 'edit':
                try:
                    with transaction.atomic():
                        instance = PlantillaPersona.objects.get(id=int(request.POST['id']))
                        form = PlantillaPersonalForm(request.POST)
                        if form.is_valid():
                            instance.persona = form.cleaned_data['persona']
                            instance.cargo = form.cleaned_data['cargo']
                            instance.coordenadamarcacion = form.cleaned_data['coordenadamarcacion']
                            instance.salario = form.cleaned_data['salario']
                            instance.fecha_ingreso = form.cleaned_data['fecha_ingreso']
                            instance.fecha_terminacion = form.cleaned_data['fecha_terminacion']
                            instance.area = form.cleaned_data['area']
                            instance.activo = form.cleaned_data['activo']
                            instance.save(request)
                            return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                        else:
                            return JsonResponse({'success': False, 'errors': form.errors})
                except Exception as e:
                    transaction.set_rollback(True)
                    return JsonResponse({'success': False})

            if action == 'eliminar':
                try:
                    instance = PlantillaPersona.objects.get(id=int(request.POST['id']))
                    instance.status = False
                    instance.save(request)
                    perfil_persona = PersonaPerfil.objects.filter(status=True, persona=instance.persona)
                    if perfil_persona.exists():
                        perfil_persona = perfil_persona.first()
                        perfil_persona.is_empleado = False
                        perfil_persona.save(request)
                    return JsonResponse({'success': True, 'message': 'Registro eliminado con éxito'})
                except Exception as ex:
                    pass

            if action == 'actualizar_estado':
                try:
                    id = int(request.POST.get('pk'))
                    estado = request.POST.get('estado')
                    instance = PlantillaPersona.objects.get(id=id)
                    instance.activo = True if estado == 'true' else False
                    instance.save(request)
                    perfil_persona = PersonaPerfil.objects.filter(status=True, persona=instance.persona)
                    if perfil_persona.exists():
                        perfil_persona = perfil_persona.first()
                        perfil_persona.is_empleado = True if estado == 'true' else False
                        perfil_persona.save(request)
                    return JsonResponse({'success': True, 'message': 'Estado actualizado con éxito'})
                except PlantillaPersona.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'El registro no existe'})

        return JsonResponse({"success": False, "mensaje": "No se ha encontrado success."})
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            if action == 'add':
                try:
                    data['titulo'] = 'Agregar nuevo empleado'
                    data['titulo_formulario'] = 'Formulario de registro de empleado'
                    data['persona_logeado'] = persona_logeado
                    form = PlantillaPersonalForm()
                    data['form'] = form
                    return render(request, "plantillapersonal/modal/add.html", data)
                except Exception as ex:
                    pass


            if action == 'edit':
                try:
                    data['titulo'] = 'Editar personal'
                    data['titulo_formulario'] = 'Formulario de editar personal'
                    data['action'] = action
                    data['persona_logeado'] = persona_logeado
                    data['filtro'] = instance = PlantillaPersona.objects.get(pk=request.GET['id'])
                    form = PlantillaPersonalForm(initial={
                        'persona': instance.persona,
                        'cargo': instance.cargo,
                        'coordenadamarcacion': instance.coordenadamarcacion,
                        'salario': instance.salario,
                        'area': instance.area,
                        'activo': instance.activo,
                        'fecha_ingreso': instance.fecha_ingreso.strftime('%Y-%m-%d') if instance.fecha_ingreso else instance.fecha_ingreso,
                        'fecha_terminacion': instance.fecha_terminacion.strftime('%Y-%m-%d') if instance.fecha_terminacion else instance.fecha_terminacion,
                    })
                    data['form'] = form
                    return render(request, "plantillapersonal/modal/add.html", data)
                except Exception as ex:
                    pass

        else:
            try:
                data['titulo'] = 'Plantilla personal'
                data['titulo_tabla'] = 'Plantilla personal'
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
                return render(request, "plantillapersonal/view.html", data)
            except Exception as ex:
                print('Error on line {}'.format(ex.exc_info()[-1].tb_lineno))