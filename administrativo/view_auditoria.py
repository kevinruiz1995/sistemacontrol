from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.utils import is_ajax
from baseapp.funciones import add_data_aplication
from baseapp.models import Persona
from administrativo.forms import PlantillaPersonalForm
from administrativo.models import Auditoria
from system.seguridad_sistema import control_entrada_modulos, log_auditoria
from django.utils.timezone import localtime

@login_required
@control_entrada_modulos
@transaction.atomic()
def view_auditoria(request):
    global ex
    data = {}
    add_data_aplication(request, data)
    usuario_logeado = request.user
    if Persona.objects.filter(usuario=usuario_logeado, status=True).exists():
        persona_logeado = Persona.objects.get(usuario=usuario_logeado, status=True)
    else:
        persona_logeado = 'SUPERUSUARIO'

    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST['action']

            if action == 'consultar_auditoria':
                try:
                    historial = Auditoria.objects.filter(status=True, modulo_id=int(request.POST['id'])).order_by('-id')
                    historial_data = [
                        {
                            "modulo": historial_.modulo.__str__(),
                            "persona": historial_.usuario.__str__(),
                            "fecha_creacion": localtime(historial_.fecha_creacion).strftime('%Y-%m-%d %H:%M:%S.%f'),
                            "contexto": historial_.contexto,
                            "tipoaccion": historial_.get_tipoaccion_display(),
                        }
                        for historial_ in historial
                    ]
                    return JsonResponse({"success": True, "historial": historial_data})
                except Exception as ex:
                    return JsonResponse({"success": False, "mensaje": 'Error al consultar historial'})

        return JsonResponse({"success": False, "mensaje": "No se ha encontrado success."})
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

        else:
            try:
                data['titulo'] = 'Auditoría del sistema'
                data['titulo_tabla'] = 'Auditoría del sistema'
                data['persona_logeado'] = persona_logeado
                filtro = (Q(status=True))
                ruta_paginado = request.path
                if 'var' in request.GET:
                    var = request.GET['var']
                    data['var'] = var
                    ruta_paginado += "?var=" + var + "&"
                    search_ = var.strip()
                    ss = search_.split(' ')
                    filtro = filtro & (Q(modulo__nombre__icontains=search_) | Q(contexto__icontains=search_))
                lista = Auditoria.objects.filter(filtro).distinct('modulo_id').order_by('modulo_id')
                paginator = Paginator(lista, 25)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                data['page_obj'] = page_obj
                return render(request, "auditoria/view.html", data)
            except Exception as ex:
                print('Error on line {}'.format(ex.exc_info()[-1].tb_lineno))