import datetime
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.utils import is_ajax
from core.core import meses
from administrativo.models import DatosFamiliares, RegistroEntradaSalidaDiario, MOTIVO_MARCACION
from administrativo.forms import DatosFamiliaresForm
from baseapp.models import Persona
from baseapp.forms import PersonaForm


@login_required
def mibiografia(request,search=None):
    try:
        persona = Persona.objects.get(id=int(request.session['idpersona']))
        context = {
            'page_titulo': "Mi biografía",
            'titulo': "Mi biografía",
            'search': search,
            'type': 'dp',
            'persona': persona
        }
        return render(request, 'mibiografia/misdatospersonales.html', context)
    except Exception as e:
        HttpResponseRedirect(f"/?info={e.__str__()}")

@login_required
def editar_mibiografia(request):
    instance = get_object_or_404(Persona, id=int(request.session['idpersona']))
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = PersonaForm(request.POST, request.FILES)
                if form.is_valid():
                    instance.nombres = form.cleaned_data['nombres']
                    instance.apellido1 = form.cleaned_data['apellido1']
                    instance.apellido2 = form.cleaned_data['apellido2']
                    instance.direccion = form.cleaned_data['direccion']
                    instance.genero = form.cleaned_data['genero']
                    instance.fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
                    instance.correo_electronico = form.cleaned_data['correo_electronico']
                    instance.telefono = form.cleaned_data['telefono']
                    instance.save(request)
                    if 'foto' in request.FILES:
                        archivo = request.FILES['foto']
                        extension = archivo._name[archivo._name.rfind("."):]
                        archivo._name = "fotoperfil_" + str(instance.id) + '_' + str(datetime.now()).replace('-', '_') + extension.lower()
                        instance.foto = archivo
                        instance.save(request)
                    return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                else:
                    return JsonResponse({'success': False, 'errors': form.errors})
        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'success': False})
    else:
        if is_ajax(request):
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
        else:
            return redirect('administrativo:listar_personas')
    form.bloquear_cedula()
    context = {
        'form': form,
    }
    return render(request, 'form_modal.html', context)

def datos_familiares(request,search=None):
    try:
        persona = Persona.objects.get(id=int(request.session['idpersona']))
        familiares = DatosFamiliares.objects.filter(status=True, persona=persona)
        context = {
            'page_titulo': "Mi biografía",
            'titulo': "Mi biografía",
            'search': search,
            'type': 'df',
            'persona': persona,
            'familiares': familiares
        }
        return render(request, 'mibiografia/datosfamiliares.html', context)
    except Exception as e:
        HttpResponseRedirect(f"/?info={e.__str__()}")

@login_required
def crear_datosfamiliares(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = DatosFamiliaresForm(request.POST)
                if form.is_valid():
                    instance = DatosFamiliares(
                        persona_id=int(request.session['idpersona']),
                        parentesco=form.cleaned_data['parentesco'],
                        nombres=form.cleaned_data['nombres'],
                        apellido1=form.cleaned_data['apellido1'],
                        apellido2=form.cleaned_data['apellido2'],
                        cedula=form.cleaned_data['cedula'],
                        fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                        genero=form.cleaned_data['genero'],
                        correo_electronico=form.cleaned_data['correo_electronico'],
                        telefono=form.cleaned_data['telefono'],
                        direccion=form.cleaned_data['direccion']
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
            form = DatosFamiliaresForm()
        else:
            return redirect('administrativo:datos_familiares')
    context = {
        'form': form,
    }
    return render(request, 'form_modal.html', context)

@login_required
def editar_datosfamiliares(request, id):
    instance = get_object_or_404(DatosFamiliares, id=id)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = DatosFamiliaresForm(request.POST, instance=instance)
                if form.is_valid():
                    instance.parentesco = form.cleaned_data['parentesco']
                    instance.nombres = form.cleaned_data['nombres']
                    instance.apellido1 = form.cleaned_data['apellido1']
                    instance.apellido2 = form.cleaned_data['apellido2']
                    instance.cedula = form.cleaned_data['cedula']
                    instance.fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
                    instance.genero = form.cleaned_data['genero']
                    instance.correo_electronico = form.cleaned_data['correo_electronico']
                    instance.telefono = form.cleaned_data['telefono']
                    instance.direccion = form.cleaned_data['direccion']
                    instance.save(request)
                    return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                else:
                    return JsonResponse({'success': False, 'errors': form.errors})
        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'success': False})
    else:
        if is_ajax(request):
            form = DatosFamiliaresForm(initial={
                                        'parentesco': instance.parentesco,
                                        'nombres': instance.nombres,
                                        'apellido1': instance.apellido1,
                                        'apellido2': instance.apellido2,
                                        'cedula': instance.cedula,
                                        'fecha_nacimiento': instance.fecha_nacimiento.strftime('%Y-%m-%d'),
                                        'genero': instance.genero,
                                        'correo_electronico': instance.correo_electronico,
                                        'telefono': instance.telefono,
                                        'direccion': instance.direccion
            })
        else:
            return redirect('administrativo:datos_familiares')
    context = {
        'form': form,
    }
    return render(request, 'form_modal.html', context)


@login_required
def eliminar_datosfamiliares(request, id):
    try:
        instance = get_object_or_404(DatosFamiliares, id=id)
        if request.method == 'POST':
            instance.eliminar_registro(request)
            return JsonResponse({'success': True, 'message': 'Registro eliminado con éxito'})
    except DatosFamiliares.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'El registro no existe'})


@login_required
def mis_marcadas(request, search=None):
    try:
        marcaciones, mes, parametros = [], None, ''
        mes = None
        if 'mes' in request.GET:
            mes = int(request.GET['mes'])
            parametros += '&mes=' + str(mes)
            marcaciones = RegistroEntradaSalidaDiario.objects.filter(status=True, empleado__persona_id=request.session['idpersona'], fecha_hora__month=mes).order_by('fecha_hora__day')
        paginator = Paginator(marcaciones, 25)
        page = request.GET.get('page')
        try:
            page_object = paginator.page(page)
        except PageNotAnInteger:
            page_object = paginator.page(1)
        except EmptyPage:
            page_object = paginator.page(paginator.num_pages)

        context = {
            'page_object': page_object,
            'page_titulo': "Mis marcaciones",
            'titulo': "Mis marcaciones",
            'MOTIVO_MARCACION': MOTIVO_MARCACION,
            'meses': meses,
            'type': 'ma',
            'mes_': mes,
            'parametros': parametros,
        }
        return render(request, 'mibiografia/mismarcaciones.html', context)
    except Exception as e:
        HttpResponseRedirect(f"/?info={e.__str__()}")