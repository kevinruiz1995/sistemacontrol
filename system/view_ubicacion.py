from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.utils import is_ajax
from system.forms import PaisForm
from system.models import Pais


@login_required
def listar_paises(request,search=None):
    try:
        paises = Pais.objects.filter(status=True)
        if search:
            paises = paises.filter(Q(nombre__icontains=search))

        paginator = Paginator(paises, 25)
        page = request.GET.get('page')
        try:
            page_object = paginator.page(page)
        except PageNotAnInteger:
            page_object = paginator.page(1)
        except EmptyPage:
            page_object = paginator.page(paginator.num_pages)

        context = {
            'page_object': page_object,
            'page_titulo': "Paises",
            'titulo': "Paises",
            'search': search
        }
        return render(request, 'ubicacion/pais/inicio.html', context)
    except Exception as e:
        HttpResponseRedirect(f"/?info={e.__str__()}")


@login_required
def crear_pais(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = PaisForm(request.POST)
                if form.is_valid():
                    instance = Pais(
                        nombre=form.cleaned_data['nombre'],
                        codigo_pais=form.cleaned_data['codigo_pais'],
                        codigo_idioma=form.cleaned_data['codigo_idioma'],
                        codigo_telefono=form.cleaned_data['codigo_telefono'],
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
            form = PaisForm()
        else:
            return redirect('sistema:listar_paises')
    context = {
        'form': form,
    }
    return render(request, 'form_modal.html', context)

@login_required
def editar_pais(request, pk):
    instance = get_object_or_404(Pais, pk=pk)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = PaisForm(request.POST, instance=instance)
                if form.is_valid():
                    instance.nombre = form.cleaned_data['nombre']
                    instance.codigo_pais = form.cleaned_data['codigo_pais']
                    instance.codigo_idioma = form.cleaned_data['codigo_idioma']
                    instance.codigo_telefono = form.cleaned_data['codigo_telefono']
                    instance.save(request)
                    return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                else:
                    return JsonResponse({'success': False, 'errors': form.errors})
        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'success': False})
    else:
        if is_ajax(request):
            form = PaisForm(instance=instance)
        else:
            return redirect('sistema:listar_paises')
    context = {
        'form': form,
    }
    return render(request, 'form_modal.html', context)

@login_required
def eliminar_pais(request, pk):
    try:
        instance = get_object_or_404(Pais, pk=pk)
        if request.method == 'POST':
            instance.eliminar_registro(request)
            return JsonResponse({'success': True, 'message': 'Registro eliminado con éxito'})
    except Pais.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'El registro no existe'})

