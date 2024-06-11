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
from administrativo.models import JornadaLaboral, DetalleJornadaLaboral
from administrativo.forms import JornadaForm, DetalleJornadaForm
from authentication.models import CustomUser


@login_required
def listar_jornadas(request,search=None):
    try:
        parametros = ''
        jornadas = JornadaLaboral.objects.filter(status=True)
        if 'search' in request.GET:
            search_ = search = request.GET['search']
            parametros += '&search=' + search_
            search_ = search_.strip()
            ss = search_.split(' ')
            jornadas = jornadas.filter(Q(nombre__icontains=search))

        paginator = Paginator(jornadas, 25)
        page = request.GET.get('page')
        try:
            page_object = paginator.page(page)
        except PageNotAnInteger:
            page_object = paginator.page(1)
        except EmptyPage:
            page_object = paginator.page(paginator.num_pages)

        context = {
            'page_object': page_object,
            'page_titulo': "Jornadas",
            'titulo': "Jornadas",
            'DIAS_SEMANA': DIAS_SEMANA,
            'search': search,
            'parametros': parametros,
        }
        return render(request, 'jornadas/inicio.html', context)
    except Exception as e:
        HttpResponseRedirect(f"/?info={e.__str__()}")

@login_required
def listar_detallejornada(request, id,search=None):
    try:
        parametros = ''
        jornada = JornadaLaboral.objects.get(id=id)
        detalles = DetalleJornadaLaboral.objects.filter(status=True, jornada=jornada)
        if 'search' in request.GET:
            search_ = search = request.GET['search']
            parametros += '&search=' + search_
            search_ = search_.strip()
            ss = search_.split(' ')
            detalles = detalles.filter(Q(dia__icontains=search))

        paginator = Paginator(detalles.order_by('dia', 'comienza', 'finaliza'), 25)
        page = request.GET.get('page')
        try:
            page_object = paginator.page(page)
        except PageNotAnInteger:
            page_object = paginator.page(1)
        except EmptyPage:
            page_object = paginator.page(paginator.num_pages)

        context = {
            'page_object': page_object,
            'page_titulo': "Detalle de jornada",
            'subobjeto': jornada,
            'titulo': "Detalle de jornada",
            'search': search,
            'parametros': parametros,
        }
        return render(request, 'jornadas/detallejornada.html', context)
    except Exception as e:
        HttpResponseRedirect(f"/?info={e.__str__()}")


@login_required
def crear_jornada(request):
    if request.method == 'POST':
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
    else:
        if is_ajax(request):
            form = JornadaForm()
        else:
            return redirect('administrativo:listar_jornadas')
    context = {
        'form': form,
    }
    return render(request, 'form_modal.html', context)

@login_required
def crear_detallejornada(request, id):
    if request.method == 'POST':
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
        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'success': False})
    else:
        if is_ajax(request):
            form = DetalleJornadaForm()
        else:
            return redirect('administrativo:listar_detallejornada')
    context = {
        'form': form,
        'id': id,
    }
    return render(request, 'form_modal.html', context)

@login_required
def editar_jornada(request, pk):
    instance = get_object_or_404(JornadaLaboral, pk=pk)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = JornadaForm(request.POST, instance=instance)
                if form.is_valid():
                    instance.nombre = form.cleaned_data['nombre']
                    instance.save(request)
                    return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                else:
                    return JsonResponse({'success': False, 'errors': form.errors})
        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'success': False})
    else:
        if is_ajax(request):
            form = JornadaForm(initial={
                'nombre': instance.nombre,
            })
        else:
            return redirect('administrativo:listar_jornadas')
    context = {
        'form': form,
    }
    return render(request, 'form_modal.html', context)

@login_required
def editar_detallejornada(request, pk):
    instance = get_object_or_404(DetalleJornadaLaboral, pk=pk)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = DetalleJornadaForm(request.POST, instance=instance)
                if form.is_valid():
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
    else:
        if is_ajax(request):
            form = DetalleJornadaForm(initial={
                'dia': instance.dia,
                'comienza': instance.comienza,
                'finaliza': instance.finaliza,
                'motivo_entrada': instance.motivo_entrada,
                'motivo_salida': instance.motivo_salida,
            })
        else:
            return redirect('administrativo:listar_detallejornada')
    context = {
        'form': form,
    }
    return render(request, 'form_modal.html', context)

@login_required
def eliminar_jornada(request, pk):
    try:
        instance = get_object_or_404(JornadaLaboral, pk=pk)
        if request.method == 'POST':
            detalles = DetalleJornadaLaboral.objects.filter(status=True, jornada=instance).update(status=False)
            instance.eliminar_registro(request)
            return JsonResponse({'success': True, 'message': 'Registro eliminado con éxito'})
    except PlantillaPersona.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'El registro no existe'})

@login_required
def eliminar_detallejornada(request, pk):
    try:
        instance = get_object_or_404(DetalleJornadaLaboral, pk=pk)
        if request.method == 'POST':
            instance.eliminar_registro(request)
            return JsonResponse({'success': True, 'message': 'Registro eliminado con éxito'})
    except PlantillaPersona.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'El registro no existe'})


