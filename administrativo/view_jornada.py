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
from baseapp.funciones import add_data_aplication
from baseapp.models import Persona
from administrativo.models import JornadaLaboral, DetalleJornadaLaboral
from administrativo.forms import JornadaForm, DetalleJornadaForm
from authentication.models import CustomUser
from system.seguridad_sistema import secure_module


@login_required
def view(request):
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
                    form = JornadaForm(request.POST)
                    if form.is_valid():
                        instance = JornadaLaboral(
                            nombre=form.cleaned_data['nombre'],
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
                    form = JornadaForm(request.POST)
                    if form.is_valid():
                        instance = JornadaLaboral.objects.get(id=request.POST['id'])
                        instance.nombre = form.cleaned_data['nombre']
                        instance.save(request)
                        return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                    else:
                        return JsonResponse({'success': False, 'errors': form.errors})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'success': False})

        if action == 'del':
            try:
                instance = JornadaLaboral.objects.get(id=int(request.POST['id']))
                instance.status = False
                instance.save(request)
                return JsonResponse({'success': True, 'message': 'Acción realizada con exito!'})
            except Exception as ex:
                return JsonResponse({'success': False, "errors": 'Error al eliminar jornada'})

        if action == 'adddetalle':
            try:
                with transaction.atomic():
                    form = DetalleJornadaForm(request.POST)
                    if form.is_valid():
                        id = int(request.POST['id'])
                        dia = form.cleaned_data['dia']
                        comienza = form.cleaned_data['comienza']
                        finaliza = form.cleaned_data['finaliza']
                        motivo_entrada = form.cleaned_data['motivo_entrada']
                        motivo_salida = form.cleaned_data['motivo_salida']
                        instance = DetalleJornadaLaboral(
                            jornada_id=id,
                            dia=dia,
                            comienza=comienza,
                            finaliza=finaliza,
                            motivo_entrada=motivo_entrada,
                            motivo_salida=motivo_salida,
                        )
                        instance.save(request)
                        return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                    else:
                        return JsonResponse({'success': False, 'errors': form.errors})
            except Exception as ex:
                return JsonResponse({'success': False, 'errors': 'Error al adicionar detalle'})

        if action == 'editdetalle':
            try:
                with transaction.atomic():
                    form = DetalleJornadaForm(request.POST)
                    if form.is_valid():
                        instance = DetalleJornadaLaboral.objects.get(id=int(request.POST['id']))
                        instance.dia = form.cleaned_data['dia']
                        instance.comienza = form.cleaned_data['comienza']
                        instance.finaliza = form.cleaned_data['finaliza']
                        instance.motivo_entrada = form.cleaned_data['motivo_entrada']
                        instance.motivo_salida = form.cleaned_data['motivo_salida']
                        instance.save(request)
                        return JsonResponse({'success': True, 'message': 'Acción realizada con exito!'})
                    else:
                        return JsonResponse({'success': False, 'errors': form.errors})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'success': False})

        if action == 'deldetalle':
            try:
                instance = DetalleJornadaLaboral.objects.get(id=int(request.POST['id']))
                instance.status = False
                instance.save(request)
                return JsonResponse({'success': True, 'message': 'Acción realizada con exito!'})
            except Exception as ex:
                return JsonResponse({'success': False, "errors": 'Error al eliminar detalle'})

    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

            if action == 'add':
                try:
                    data['titulo'] = 'Agregar nueva jornada'
                    data['titulo_formulario'] = 'Formulario de registro de jornada'
                    form = JornadaForm()
                    data['form'] = form
                    return render(request, "jornadas/modal/add.html", data)
                except Exception as ex:
                    pass

            if action == 'edit':
                try:
                    data['titulo'] = 'Editar jornada'
                    data['titulo_formulario'] = 'Edición de jornada'
                    data['filtro'] = filtro = JornadaLaboral.objects.get(pk=request.GET['id'])
                    form = JornadaForm(initial={
                        'nombre': filtro.nombre
                    })
                    data['form'] = form
                    return render(request, "jornadas/modal/add.html", data)
                except Exception as ex:
                    pass

            if action == 'detallejornada':
                try:
                    data['titulo'] = 'Detalle de jornada'
                    data['titulo_tabla'] = 'Lista  de detalles'
                    jornada = JornadaLaboral.objects.get(id=request.GET['id'])
                    filtro = (Q(status=True) & Q(jornada=jornada))
                    ruta_paginado = request.path
                    if 'var' in request.GET:
                        var = request.GET['var']
                        data['var'] = var
                        filtro = filtro & (Q(dia__icontains=var))
                        ruta_paginado += "?var=" + var + "&"
                    detalles = DetalleJornadaLaboral.objects.filter(filtro).order_by('dia', 'comienza', 'finaliza')
                    lista = JornadaLaboral.objects.filter(status=True)
                    paginator = Paginator(lista, 25)
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                    data['page_obj'] = page_obj
                    return render(request, "jornadas/detallejornada.html", data)
                except Exception as ex:
                    pass

        else:
            try:
                data['titulo'] = 'Jornadas'
                data['titulo_tabla'] = 'Lista  de jornadas'
                data['persona_logeado'] = persona_logeado
                filtro = (Q(status=True))
                ruta_paginado = request.path
                if 'var' in request.GET:
                    var = request.GET['var']
                    data['var'] = var
                    filtro = filtro & (Q(nombre__icontains=var))
                    ruta_paginado += "?var=" + var + "&"
                lista = JornadaLaboral.objects.filter(filtro).order_by('id')
                paginator = Paginator(lista, 25)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                data['page_obj'] = page_obj
                data['DIAS_SEMANA'] = DIAS_SEMANA
                return render(request, "jornadas/view.html", data)
            except Exception as ex:
                print('Error on line {}'.format(ex.exc_info()[-1].tb_lineno))


