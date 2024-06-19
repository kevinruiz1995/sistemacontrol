import datetime
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.utils import is_ajax
from core.core import DIAS_SEMANA
from baseapp.funciones import add_data_aplication
from baseapp.models import Persona
from administrativo.models import ConfiguracionCoordenadaMarcacion
from administrativo.forms import ConfiguracionCoordenadaForm
from authentication.models import CustomUser
from system.seguridad_sistema import secure_module


@login_required
def view_configuracioncoordenada(request):
    global ex
    data = {}
    add_data_aplication(request, data)
    usuario_logeado = request.user
    if 'tipoperfil' in request.session:
        tipoperfil = request.session['tipoperfil']
    else:
        tipoperfil = usuario_logeado.groups.all()
    consulta_logeo = Persona.objects.filter(usuario=usuario_logeado, status=True)
    if consulta_logeo.exists():
        persona_logeado = consulta_logeo.first()
    else:
        persona_logeado = 'SUPERUSUARIO'
    if request.method == 'POST':
        data['action'] = action = request.POST['action']

        if action == 'add':
            try:
                with transaction.atomic():
                    form = ConfiguracionCoordenadaForm(request.POST)
                    if form.is_valid():
                        instance = ConfiguracionCoordenadaMarcacion(
                            nombre=form.cleaned_data['nombre'],
                            latitud=form.cleaned_data['latitud'],
                            longitud=form.cleaned_data['longitud'],
                            radio=form.cleaned_data['radio'],
                        )
                        instance.save(request)
                        return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                    else:
                        return JsonResponse({'success': False, 'errors': form.errors})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'success': False})

        if action == 'edit':
            try:
                with transaction.atomic():
                    form = ConfiguracionCoordenadaForm(request.POST)
                    if form.is_valid():
                        instance = ConfiguracionCoordenadaMarcacion.objects.get(id=request.POST['id'])
                        instance.nombre = form.cleaned_data['nombre']
                        instance.latitud = form.cleaned_data['latitud']
                        instance.longitud = form.cleaned_data['longitud']
                        instance.radio = form.cleaned_data['radio']
                        instance.save(request)
                        return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                    else:
                        return JsonResponse({'success': False, 'errors': form.errors})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'success': False})

        if action == 'del':
            try:
                instance = ConfiguracionCoordenadaMarcacion.objects.get(id=int(request.POST['id']))
                instance.status = False
                instance.save(request)
                return JsonResponse({'success': True, 'message': 'Acción realizada con exito!'})
            except Exception as ex:
                return JsonResponse({'success': False, "errors": 'Error al eliminar jornada'})

    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

            if action == 'add':
                try:
                    data['titulo'] = 'Agregar nueva configuración de coordenadas'
                    data['titulo_formulario'] = 'Formulario de registro de coordenadas '
                    form = ConfiguracionCoordenadaForm()
                    data['form'] = form
                    return render(request, "configuracioncoordenada/modal/add.html", data)
                except Exception as ex:
                    pass

            if action == 'edit':
                try:
                    data['titulo'] = 'Editar configuración de coordenadas'
                    data['titulo_formulario'] = 'Edición de coordenadas'
                    data['filtro'] = filtro = ConfiguracionCoordenadaMarcacion.objects.get(pk=request.GET['id'])
                    form = ConfiguracionCoordenadaForm(initial={
                        'nombre': filtro.nombre,
                        'latitud': filtro.latitud,
                        'longitud': filtro.longitud,
                        'radio': filtro.radio,
                    })
                    data['form'] = form
                    return render(request, "configuracioncoordenada/modal/add.html", data)
                except Exception as ex:
                    pass

        else:
            try:
                data['titulo'] = 'Coordenadas'
                data['titulo_tabla'] = 'Lista  de coordenadas'
                data['persona_logeado'] = persona_logeado
                filtro = (Q(status=True))
                ruta_paginado = request.path
                if 'var' in request.GET:
                    var = request.GET['var']
                    data['var'] = var
                    filtro = filtro & (Q(nombre__icontains=var))
                    ruta_paginado += "?var=" + var + "&"
                lista = ConfiguracionCoordenadaMarcacion.objects.filter(filtro).order_by('id')
                paginator = Paginator(lista, 25)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                data['page_obj'] = page_obj
                data['DIAS_SEMANA'] = DIAS_SEMANA
                return render(request, "configuracioncoordenada/view.html", data)
            except Exception as ex:
                print('Error on line {}'.format(ex.exc_info()[-1].tb_lineno))


