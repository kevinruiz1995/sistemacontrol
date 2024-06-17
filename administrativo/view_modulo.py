import sys
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render

from sistemacontrol.settings import MEDIA_URL
from system.forms import ModuloForm
from system.models import Modulo
from baseapp.funciones import add_data_aplication
from administrativo.models import Persona


@login_required(redirect_field_name='next', login_url='/login')
@transaction.atomic()
def view_modulo(request):
    global ex
    data = {}
    add_data_aplication(request, data)
    usuario_logeado = request.user
    if Persona.objects.filter(usuario=usuario_logeado, status=True).exists():
        persona_logeado = Persona.objects.get(usuario=usuario_logeado, status=True)
    else:
        persona_logeado = 'CAM'

    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST['action']
            if action == 'add_modulo':
                try:
                    form = ModuloForm(request.POST, request.FILES)
                    if form.is_valid():
                        campos_repetidos = list()

                        if Modulo.objects.values('id').filter(status=True, nombre=form.cleaned_data['nombre']).exists():
                            campos_repetidos.append(form['nombre'].name)
                        if Modulo.objects.values('id').filter(status=True, url_name=form.cleaned_data['url_name']).exists():
                            campos_repetidos.append(form['url_name'].name)
                        if campos_repetidos:
                            return JsonResponse({"success": False, "mensaje": "registro ya existe.",'repetidos':campos_repetidos})
                        modulo = Modulo(
                            categoria=form.cleaned_data['categoria'],
                            nombre=form.cleaned_data['nombre'],
                            descripcion=form.cleaned_data['descripcion'],
                            logo=form.cleaned_data['logo'],
                            url_name=form.cleaned_data['url_name'],
                            activo=form.cleaned_data['activo']
                        )
                        modulo.save(request)
                        return JsonResponse({"success": True, "mensaje": "Registro guardado correctamente."})

                    else:
                        return JsonResponse({"success": False, "mensaje": str(form.errors.items())})

                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"success": False, "mensaje": "Ha ocurrido un error, intente más tarde."})

            if action == 'edit_modulo':
                try:
                    form = ModuloForm(request.POST, request.FILES)
                    form.editar()
                    if form.is_valid():
                        campos_repetidos = list()
                        if Modulo.objects.values('id').filter(status=True, nombre=form.cleaned_data['nombre']).exclude(pk=request.POST['id']).exists():
                            campos_repetidos.append(form['nombre'].name)
                        if Modulo.objects.values('id').filter(status=True, url_name=form.cleaned_data['url_name']).exclude(pk=request.POST['id']).exists():
                            campos_repetidos.append(form['url_name'].name)
                        if campos_repetidos:
                            return JsonResponse({"success": False, "mensaje": "registro ya existe.",
                                                     'repetidos': campos_repetidos})
                        modulo = Modulo.objects.get(pk=request.POST['id'])
                        modulo.categoria = form.cleaned_data['categoria']
                        modulo.nombre = form.cleaned_data['nombre']
                        modulo.descripcion = form.cleaned_data['descripcion']
                        if form.cleaned_data['logo']:
                            modulo.logo = form.cleaned_data['logo']
                        else:
                            modulo.logo = request.POST['imagen_url_name']
                        modulo.url_name = form.cleaned_data['url_name']
                        modulo.activo = form.cleaned_data['activo']
                        modulo.save(request)

                        return JsonResponse({"success": True, "mensaje": "Registro Modificado correctamente."})
                    else:
                        return JsonResponse({"success": False, "mensaje": form.errors.items()})


                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"success": False, "mensaje": "Ha ocurrido un error, intente más tarde."})

            if action == 'eliminar_modulo':
                try:
                    with transaction.atomic():
                        registro = Modulo.objects.get(pk=request.POST['id'])
                        registro.status = False
                        registro.save(request)
                        return JsonResponse({"success": True, "mensaje": "Registro eliminado correctamente."})

                except Exception as ex:
                    pass

        return JsonResponse({"success": False, "mensaje": "No se ha encontrado success."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add_modulo':
                try:
                    data['titulo'] = 'Agregar nuevo módulo'
                    data['titulo_formulario'] = 'Formulario de registro de Módulo'
                    data['action'] = 'add_modulo'
                    data['persona_logeado'] = persona_logeado
                    form= ModuloForm()
                    form.add()
                    data['form'] = form
                    return render(request, "conf_sistema/add_modulo.html", data)
                except Exception as ex:
                    pass


            if action == 'edit_modulo':
                try:
                    data['titulo'] = 'Editar módulo'
                    data['titulo_formulario'] = 'Formulario de editar Módulo'
                    data['action'] = 'edit_modulo'
                    data['persona_logeado'] = persona_logeado
                    data['MEDIA_URL'] = MEDIA_URL
                    data['modulo'] = modulo = Modulo.objects.get(pk=request.GET['id'])
                    data['form'] = form = ModuloForm(initial=model_to_dict(modulo))
                    return render(request, "conf_sistema/edit_modulo.html", data)
                except Exception as ex:
                    pass

        else:
            try:
                data['titulo'] = 'Configuración de Módulos'
                data['titulo_tabla'] = 'Lista  de Módulos'
                data['persona_logeado'] = persona_logeado
                lista = Modulo.objects.filter(status=True).order_by('id')
                paginator = Paginator(lista, 25)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                data['page_obj'] = page_obj
                return render(request, "conf_sistema/view_modulo.html", data)
            except Exception as ex:
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
