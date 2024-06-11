from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

from core.helper_response import HelperJsonResponse
from core.utils import is_ajax
from system.forms import CategoriaModuloForm, ModuloForm
from system.models import CategoriaModulo, Modulo


@login_required
def listar_categoria_modulo(request,search=None):
    try:
        categorias = CategoriaModulo.objects.filter(status=True).order_by('orden')
        if search:
            categorias = categorias.filter(Q(nombre__icontains=search))

        paginator = Paginator(categorias, 25)
        page = request.GET.get('page')
        try:
            page_object = paginator.page(page)
        except PageNotAnInteger:
            page_object = paginator.page(1)
        except EmptyPage:
            page_object = paginator.page(paginator.num_pages)

        context = {
            'page_object': page_object,
            'page_titulo': "Categoría Módulos",
            'titulo': "Categoría Módulos",
            'search': search
        }
        return render(request, 'categoriamodulo/inicio.html', context)
    except Exception as e:
        HttpResponseRedirect(f"/?info={e.__str__()}")

@login_required
def crear_categoria_modulo(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = CategoriaModuloForm(request.POST)
                if form.is_valid():
                    instance = CategoriaModulo(
                        nombre=form.cleaned_data['nombre'],
                        descripcion=form.cleaned_data['descripcion'],
                        visible=form.cleaned_data['visible'],
                        orden=form.cleaned_data['orden'],
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
            form = CategoriaModuloForm()
        else:
            return redirect('sistema:listar_categoria_modulo')
    context = {
        'form': form,
    }
    return render(request, 'form_modal.html', context)

@login_required
def editar_categoria_modulo(request, pk):
    instance = get_object_or_404(CategoriaModulo, pk=pk)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = CategoriaModuloForm(request.POST, instance=instance)
                if form.is_valid():
                    instance.nombre = form.cleaned_data['nombre']
                    instance.descripcion = form.cleaned_data['descripcion']
                    instance.visible = form.cleaned_data['visible']
                    instance.orden = form.cleaned_data['orden']
                    instance.save(request)
                    return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                else:
                    return JsonResponse({'success': False, 'errors': form.errors})
        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'success': False})
    else:
        if is_ajax(request):
            form = CategoriaModuloForm(instance=instance)
        else:
            return redirect('sistema:listar_categoria_modulo')
    context = {
        'form': form,
        'object_list': instance,
    }
    return render(request, 'form_modal.html', context)

@login_required
def eliminar_categoria_modulo(request, pk):
    try:
        instance = get_object_or_404(CategoriaModulo, pk=pk)
        if request.method == 'POST':
            instance.eliminar_registro(request)
            return JsonResponse({'success': True, 'message': 'Registro eliminado con éxito'})
    except CategoriaModulo.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'El registro no existe'})



@login_required
def listar_modulo(request,search=None):
    try:
        modulos = Modulo.objects.filter(status=True).order_by('orden')
        if search:
            modulos = modulos.filter(Q(nombre__icontains=search))

        paginator = Paginator(modulos, 25)
        page = request.GET.get('page')
        try:
            page_object = paginator.page(page)
        except PageNotAnInteger:
            page_object = paginator.page(1)
        except EmptyPage:
            page_object = paginator.page(paginator.num_pages)

        context = {
            'page_object': page_object,
            'page_titulo': "Módulos",
            'titulo': "Módulos",
            'search': search
        }
        return render(request, 'modulo/inicio.html', context)
    except Exception as e:
        HttpResponseRedirect(f"/?info={e.__str__()}")

@login_required
def crear_modulo(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = ModuloForm(request.POST)
                if form.is_valid():
                    instance = Modulo(
                        categoria=form.cleaned_data['categoria'],
                        nombre=form.cleaned_data['nombre'],
                        icono=form.cleaned_data['icono'],
                        descripcion=form.cleaned_data['descripcion'],
                        url_name=form.cleaned_data['url_name'],
                        visible=form.cleaned_data['visible'],
                        orden=form.cleaned_data['orden'],
                        es_modulo_padre=form.cleaned_data['es_modulo_padre'],
                    )
                    instance.save(request)
                    return HelperJsonResponse(success=True, data={}, message='Acción realizada con éxito!', status=200)
                else:
                    return HelperJsonResponse(success=False, data={'errors': form.errors}, message=f'Los datos ingresados no son validos', status=200)
        except Exception as e:
            transaction.set_rollback(True)
            return HelperJsonResponse(success=False, data={}, message=f'Ha ocurrio un error: {e.__str__()}', status=200)
    else:
        if is_ajax(request):
            form = ModuloForm()
        else:
            return redirect('sistema:listar_modulo')
    context = {
        'form': form,
    }
    return render(request, 'modulo/modal_modulo.html', context)

@login_required
def editar_modulo(request, pk):
    instance = get_object_or_404(Modulo, pk=pk)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = ModuloForm(request.POST, instance=instance)
                if form.is_valid():
                    instance.categoria = form.cleaned_data['categoria']
                    instance.nombre = form.cleaned_data['nombre']
                    instance.es_modulo_padre = form.cleaned_data['es_modulo_padre']
                    instance.icono = form.cleaned_data['icono']
                    instance.url_name = form.cleaned_data['url_name']
                    instance.descripcion = form.cleaned_data['descripcion']
                    instance.visible = form.cleaned_data['visible']
                    instance.orden = form.cleaned_data['orden']
                    instance.save(request)
                    return HelperJsonResponse(success=True, data={}, message='Acción realizada con éxito!', status=200)
                else:
                    return HelperJsonResponse(success=False, data={'errors': form.errors}, message=f'Los datos ingresados no son validos', status=200)
        except Exception as e:
            transaction.set_rollback(True)
            return HelperJsonResponse(success=False, data={}, message=f'Ha ocurrio un error: {e.__str__()}', status=200)
    else:
        if is_ajax(request):
            form = ModuloForm(instance=instance)
        else:
            return redirect('sistema:listar_modulo')
    context = {
        'form': form,
        'instance': instance,
    }
    return render(request, 'modulo/modal_modulo.html', context)

@login_required
def eliminar_modulo(request, pk):
    try:
        instance = get_object_or_404(Modulo, pk=pk)
        if request.method == 'POST':
            instance.eliminar_registro(request)
            return HelperJsonResponse(success=True, data={}, message='Registro eliminado con éxito!', status=200)
    except Modulo.DoesNotExist:
        return HelperJsonResponse(success=False, data={}, message=f'El registro no existe', status=200)