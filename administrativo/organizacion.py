from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.utils import is_ajax
from administrativo.forms import DatosOrganizacionForm
from administrativo.models import DatosOrganizacion
from baseapp.forms import PersonaForm
from authentication.models import CustomUser

@login_required
def editar_organizacion(request):
    instance = DatosOrganizacion.objects.filter(status=True)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = DatosOrganizacionForm(request.POST)
                if form.is_valid():
                    if instance.exists():
                        instance = instance.first()
                        form.instance = instance
                        instance.nombre = form.cleaned_data['nombre']
                        instance.direccion = form.cleaned_data['direccion']
                        instance.latitud = form.cleaned_data['latitud']
                        instance.longitud = form.cleaned_data['longitud']
                        instance.radio = form.cleaned_data['radio']
                        instance.save(request)
                    else:
                        instance = DatosOrganizacion(nombre = form.cleaned_data['nombre'],
                                                     direccion = form.cleaned_data['direccion'],
                                                     latitud = form.cleaned_data['latitud'],
                                                     longitud = form.cleaned_data['longitud'],
                                                     radio = form.cleaned_data['radio'])
                        instance.save(request)
                    return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                else:
                    return JsonResponse({'success': False, 'errors': form.errors})
        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'success': False})
    else:
        form = DatosOrganizacionForm()
        if instance.exists():
            instance = instance.first()
            form = DatosOrganizacionForm(initial={
                                        'nombre': instance.nombre,
                                        'direccion': instance.direccion,
                                        'latitud': instance.latitud,
                                        'longitud': instance.longitud,
                                        'radio': instance.radio,
            })
    context = {
        'form': form,
        'page_titulo': 'Organización',
        'titulo': 'Organización',
    }
    return render(request, 'organizacion/inicio.html', context)
