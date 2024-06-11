from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.utils import is_ajax
from administrativo.forms import PlantillaPersonalForm
from administrativo.models import PlantillaPersona, PersonaPerfil


@login_required
def listar_personal(request,search=None):
    try:
        parametros = ''
        personal = PlantillaPersona.objects.filter(status=True)
        if 'search' in request.GET:
            search_ = search = request.GET['search']
            parametros += '&search=' + search_
            search_ = search_.strip()
            ss = search_.split(' ')
            if len(ss) == 1:
                personal = personal.filter(Q(persona__nombres__icontains=search) |
                                           Q(persona__apellido1__icontains=search) |
                                           Q(persona__apellido2__icontains=search) |
                                           Q(persona__cedula__icontains=search) |
                                           Q(persona__pasaporte__icontains=search))
            else:
                personal = personal.filter((Q(persona__apellido1__icontains=ss[0]) & Q(persona__apellido2__icontains=ss[1])) |
                                           (Q(persona__nombres__icontains=ss[0]) & Q(persona__nombres__icontains=ss[1])))

        paginator = Paginator(personal, 25)
        page = request.GET.get('page')
        try:
            page_object = paginator.page(page)
        except PageNotAnInteger:
            page_object = paginator.page(1)
        except EmptyPage:
            page_object = paginator.page(paginator.num_pages)

        context = {
            'page_object': page_object,
            'page_titulo': "Plantilla personal",
            'titulo': "Plantilla personal",
            'search': search,
            'parametros': parametros,
        }
        return render(request, 'plantillapersonal/listar.html', context)
    except Exception as e:
        HttpResponseRedirect(f"/?info={e.__str__()}")


@login_required
def crear_personal(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = PlantillaPersonalForm(request.POST)
                if form.is_valid():
                    instance = PlantillaPersona(
                        persona=form.cleaned_data['persona'],
                        cargo=form.cleaned_data['cargo'],
                        salario=form.cleaned_data['salario'],
                        fecha_ingreso=form.cleaned_data['fecha_ingreso'],
                        fecha_terminacion=form.cleaned_data['fecha_terminacion'],
                        area=form.cleaned_data['area'],
                        activo=form.cleaned_data['activo'],
                    )
                    instance.save(request)
                    perfil_persona = PersonaPerfil.objects.filter(status=True, persona=form.cleaned_data['persona'])
                    if perfil_persona.exists():
                        perfil_persona = perfil_persona.first()
                        perfil_persona.is_empleado = True
                        perfil_persona.save(request)
                    return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                else:
                    return JsonResponse({'success': False, 'errors': form.errors})
        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'success': False})
    else:
        if is_ajax(request):
            form = PlantillaPersonalForm()
        else:
            return redirect('administrativo:listar_personal')
    context = {
        'form': form,
    }
    return render(request, 'form_modal.html', context)

@login_required
def editar_personal(request, pk):
    instance = get_object_or_404(PlantillaPersona, pk=pk)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = PlantillaPersonalForm(request.POST, instance=instance)
                if form.is_valid():
                    instance.persona = form.cleaned_data['persona']
                    instance.cargo = form.cleaned_data['cargo']
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
    else:
        if is_ajax(request):
            form = PlantillaPersonalForm(initial={
                                        'persona': instance.persona,
                                        'cargo': instance.cargo,
                                        'salario': instance.salario,
                                        'area': instance.area,
                                        'activo': instance.activo,
                                        'fecha_ingreso': instance.fecha_ingreso.strftime('%Y-%m-%d'),
                                        'fecha_terminacion': instance.fecha_terminacion.strftime('%Y-%m-%d'),
            })
        else:
            return redirect('administrativo:listar_personal')
    context = {
        'form': form,
    }
    return render(request, 'form_modal.html', context)

@login_required
def eliminar_personal(request, pk):
    try:
        instance = get_object_or_404(PlantillaPersona, pk=pk)
        if request.method == 'POST':
            instance.eliminar_registro(request)
            perfil_persona = PersonaPerfil.objects.filter(status=True, persona=instance.persona)
            if perfil_persona.exists():
                perfil_persona = perfil_persona.first()
                perfil_persona.is_empleado = False
                perfil_persona.save(request)
            return JsonResponse({'success': True, 'message': 'Registro eliminado con éxito'})
    except PlantillaPersona.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'El registro no existe'})

@login_required
def actualizar_estado(request):
    try:
        pk = int(request.POST.get('pk'))
        estado = request.POST.get('estado')
        instance = get_object_or_404(PlantillaPersona, pk=pk)
        if request.method == 'POST':
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

