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


@login_required
def listar_mismarcaciones(request,search=None):
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
            'mes_': mes,
            'parametros': parametros,
        }
        return render(request, 'mismarcaciones/inicio.html', context)
    except Exception as e:
        HttpResponseRedirect(f"/?info={e.__str__()}")

