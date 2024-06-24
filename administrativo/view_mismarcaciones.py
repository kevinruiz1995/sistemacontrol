from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q, Count, Value
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.utils import is_ajax
from core.core import meses
from administrativo.forms import PlantillaPersonalForm
from administrativo.models import RegistroEntradaSalidaDiario, MOTIVO_MARCACION
from system.seguridad_sistema import control_entrada_modulos
from baseapp.funciones import add_data_aplication
from baseapp.models import Persona


@login_required
@control_entrada_modulos
@transaction.atomic()
def view_mismarcaciones(request):
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

        return JsonResponse({"success": False, "mensaje": "No se ha encontrado success."})
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

        else:
            try:
                data['titulo'] = 'Mis marcaciones'
                data['titulo_tabla'] = 'Mis marcaciones'
                data['persona_logeado'] = persona_logeado
                ruta_paginado = request.path
                resultados = []
                if 'mes' in request.GET:
                    mes = int(request.GET['mes'])
                    data['mes_'] = int(request.GET['mes'])
                    ruta_paginado += "?mes_=" + request.GET['mes'] + "&"
                    resultados = RegistroEntradaSalidaDiario.objects.filter(status=True, empleado__persona_id=request.session['idpersona'], fecha_hora__month=mes).order_by('fecha_hora__day')
                lista = resultados
                paginator = Paginator(lista, 25)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                data['page_obj'] = page_obj
                data['MOTIVO_MARCACION'] = MOTIVO_MARCACION
                data['meses'] = meses
                return render(request, "mismarcaciones/view.html", data)
            except Exception as ex:
                print('Error on line {}'.format(ex.exc_info()[-1].tb_lineno))