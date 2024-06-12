import sys
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render

from system.forms import AccesoModuloForm
from baseapp.funciones import add_data_aplication
from system.models import AccesoModulo
from administrativo.models import Persona


@login_required(redirect_field_name='next', login_url='/login')
@transaction.atomic()
def view_acceso_modulo(request):
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
            if action == 'add_acceso_modulo':
                try:
                    form = AccesoModuloForm(request.POST, request.FILES)
                    if form.is_valid():
                        grupo = form.cleaned_data['grupo']
                        modulo = form.cleaned_data['modulo']
                        activo = form.cleaned_data['activo']

                        registro = AccesoModulo(
                            grupo= grupo,
                            modulo = modulo,
                            activo = activo
                        )
                        registro.save(request)
                    else:
                       return JsonResponse({"success": False, "mensaje": form.errors.items()})

                    return JsonResponse({"success": True, "mensaje": "Registro guardado correctamente."})
                except Exception as ex:
                    pass


            if action == 'eliminar_acceso_modulo':
                try:
                    with transaction.atomic():
                        registro = AccesoModulo.objects.get(pk=request.POST['id'])
                        registro.status = False
                        registro.save(request)
                        return JsonResponse({"success": True, "mensaje": "Registro eliminado correctamente."})

                except Exception as ex:
                    pass


        return JsonResponse({"success": False, "mensaje": "acción Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'desactivar_acceso':
                try:
                    acceso = AccesoModulo.objects.get(pk= request.GET['id'])
                    acceso.activo =False
                    acceso.save(request)
                    return JsonResponse({"success": True, "mensaje": "desactivado correctamente."})
                except Exception as ex:
                    pass

            if action == 'activar_acceso':
                try:
                    acceso = AccesoModulo.objects.get(pk= request.GET['id'])
                    acceso.activo =True
                    acceso.save(request)
                    return JsonResponse({"success": True, "mensaje": "desactivado correctamente."})
                except Exception as ex:
                    pass

            if action == 'add_acceso_modulo':
                try:
                    data['titulo'] = 'Agregar nuevo acceso a módulo'
                    data['titulo_formulario'] = 'Formulario de registro de acceso a módulo'
                    data['action'] = 'add_acceso_modulo'
                    data['persona_logeado'] = persona_logeado
                    form = AccesoModuloForm()
                    data['form'] = form


                    return render(request, "conf_sistema/add_acceso_modulo.html", data)
                except Exception as ex:
                    pass
        else:
            try:
                data['titulo'] = 'Configuración de acceso a módulos'
                data['titulo_tabla'] = 'Lista  de acceso a módulos'
                data['persona_logeado'] = persona_logeado
                lista = AccesoModulo.objects.filter(status=True).order_by('id')
                paginator = Paginator(lista, 25)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                data['page_obj'] = page_obj

                return render(request, "conf_sistema/view_acceso_modulo.html", data)
            except Exception as ex:
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
