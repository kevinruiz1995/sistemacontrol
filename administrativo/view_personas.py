import datetime
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.utils import is_ajax
from administrativo.forms import PlantillaPersonalForm
from administrativo.models import PlantillaPersona, Persona, PersonaPerfil
from baseapp.forms import PersonaForm
from baseapp.funciones import add_data_aplication
from authentication.models import CustomUser
from system.seguridad_sistema import control_entrada_modulos


@login_required
@control_entrada_modulos
@transaction.atomic()
def view_persona(request):
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
                    form = PersonaForm(request.POST, request.FILES)
                    if form.is_valid():
                        instance = Persona(
                            nombres=form.cleaned_data['nombres'],
                            apellido1=form.cleaned_data['apellido1'],
                            apellido2=form.cleaned_data['apellido2'],
                            cedula=form.cleaned_data['cedula'],
                            pasaporte=form.cleaned_data['pasaporte'],
                            ruc=form.cleaned_data['ruc'],
                            direccion=form.cleaned_data['direccion'],
                            genero=form.cleaned_data['genero'],
                            fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                            correo_electronico=form.cleaned_data['correo_electronico'],
                            telefono=form.cleaned_data['telefono'],
                        )
                        instance.save(request)
                        if 'foto' in request.FILES:
                            archivo = request.FILES['foto']
                            archivo._name = "fotoperfil_" + str(instance.id) + '_' + str(datetime.now())
                            instance.foto = archivo
                            instance.save(request)
                        identificacion = '*'
                        if instance.cedula:
                            identificacion = instance.cedula
                        elif instance.pasaporte:
                            identificacion = instance.pasaporte
                        elif instance.ruc:
                            identificacion = instance.ruc
                        password = identificacion.replace(' ', '')
                        password = password.lower()
                        username = form.cleaned_data['nombres'].replace(' ', '').lower()  # Eliminar espacios y líneas nuevas
                        usuario = CustomUser.objects.create_user(username, password)
                        usuario.save()
                        instance.usuario = usuario
                        instance.save(request)
                        persona_perfil = PersonaPerfil(
                            persona=instance
                        )
                        persona_perfil.save(request)
                        return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                    else:
                        return JsonResponse({"success": False, "mensaje": str(form.errors.items())})

                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"success": False, "mensaje": "Ha ocurrido un error, intente más tarde."})

            if action == 'edit':
                try:
                    with transaction.atomic():
                        form = PersonaForm(request.POST, request.FILES)
                        if form.is_valid():
                            instance = Persona.objects.get(id=int(request.POST['id']))
                            instance.nombres = form.cleaned_data['nombres']
                            instance.apellido1 = form.cleaned_data['apellido1']
                            instance.apellido2 = form.cleaned_data['apellido2']
                            if request.session['administrador_principal']:
                                instance.cedula = form.cleaned_data['cedula']
                                instance.pasaporte = form.cleaned_data['pasaporte']
                                instance.ruc = form.cleaned_data['ruc']
                            instance.direccion = form.cleaned_data['direccion']
                            instance.genero = form.cleaned_data['genero']
                            instance.fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
                            instance.correo_electronico = form.cleaned_data['correo_electronico']
                            instance.telefono = form.cleaned_data['telefono']
                            instance.save(request)
                            if 'foto' in request.FILES:
                                archivo = request.FILES['foto']
                                extension = archivo._name[archivo._name.rfind("."):]
                                archivo._name = "fotoperfil_" + str(instance.id) + '_' + str(datetime.now()).replace(
                                    '-', '_') + extension.lower()
                                instance.foto = archivo
                                instance.save(request)
                            return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                        else:
                            return JsonResponse({'success': False, 'errors': form.errors})
                except Exception as e:
                    transaction.set_rollback(True)
                    return JsonResponse({'success': False})

            if action == 'eliminar':
                try:
                    with transaction.atomic():
                        registro = Persona.objects.get(pk=request.POST['id'])
                        registro.status = False
                        registro.save(request)
                        return JsonResponse({"success": True, "mensaje": "Registro eliminado correctamente."})

                except Exception as ex:
                    pass

            if action == 'activar_desactivar_perfil':
                try:
                    id = int(request.POST['pk'])
                    tipo = int(request.POST['tipo'])
                    estado = int(request.POST['estado'])
                    estado = True if estado == 1 else False
                    perfil_persona = PersonaPerfil.objects.filter(status=True, persona_id=id)
                    if perfil_persona.exists():
                        perfil_persona = perfil_persona.first()
                        # PERFIL TIPO ADMINISTRATIVO
                        if tipo == 1:
                            perfil_persona.is_administrador = estado
                            perfil_persona.save(request)
                        elif tipo == 2:
                            perfil_persona.is_empleado = estado
                            perfil_persona.save(request)
                        elif tipo == 3:
                            perfil_persona.is_jefe_departamental = estado
                            perfil_persona.save(request)

                    return JsonResponse({'success': True, 'message': 'Acción realizada con éxito'})
                except PersonaPerfil.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'El registro no existe'})

        return JsonResponse({"success": False, "mensaje": "No se ha encontrado success."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    data['titulo'] = 'Agregar nueva persona'
                    data['titulo_formulario'] = 'Formulario de registro de persona'
                    data['action'] = action
                    data['persona_logeado'] = persona_logeado
                    form = PersonaForm()
                    data['form'] = form
                    return render(request, "personas/modal/add.html", data)
                except Exception as ex:
                    pass


            if action == 'edit':
                try:
                    data['titulo'] = 'Editar persona'
                    data['titulo_formulario'] = 'Formulario de editar persona'
                    data['action'] = action
                    data['persona_logeado'] = persona_logeado
                    data['filtro'] = instance = Persona.objects.get(pk=request.GET['id'])
                    form = PersonaForm(initial={
                        'nombres': instance.nombres,
                        'apellido1': instance.apellido1,
                        'apellido2': instance.apellido2,
                        'cedula': instance.cedula,
                        'pasaporte': instance.pasaporte,
                        'ruc': instance.ruc,
                        'direccion': instance.direccion,
                        'genero': instance.genero,
                        'fecha_nacimiento': instance.fecha_nacimiento.strftime('%Y-%m-%d'),
                        'correo_electronico': instance.correo_electronico,
                        'telefono': instance.telefono,
                        'foto': instance.foto,
                    })
                    data['form'] = form
                    return render(request, "personas/modal/add.html", data)
                except Exception as ex:
                    pass

        else:
            try:
                data['titulo'] = 'Lista de personas'
                data['titulo_tabla'] = 'Lista  de personas'
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
                        filtro = filtro & (Q(nombres__icontains=search_) |
                                                   Q(apellido1__icontains=search_) |
                                                   Q(apellido2__icontains=search_) |
                                                   Q(cedula__icontains=search_) |
                                                   Q(pasaporte__icontains=search_))
                    else:
                        filtro = filtro & ((Q(apellido1__icontains=ss[0]) & Q(apellido2__icontains=ss[1])) |
                                                   (Q(nombres__icontains=ss[0]) & Q(nombres__icontains=ss[1])))
                lista = Persona.objects.filter(filtro).order_by('id')
                paginator = Paginator(lista, 25)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                data['page_obj'] = page_obj
                return render(request, "personas/view.html", data)
            except Exception as ex:
                print('Error on line {}'.format(ex.exc_info()[-1].tb_lineno))

