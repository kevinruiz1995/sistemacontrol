import datetime
from datetime import datetime, date
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from baseapp.models import Persona
from baseapp.funciones import add_data_aplication
from system.models import Modulo, AccesoModulo, CategoriaModulo
from baseapp.models import Persona
from administrativo.models import PersonaPerfil, PlantillaPersona, JornadaEmpleado, DetalleRegistroEntradaSalida


@login_required # Este decorador asegura que solo los usuarios autenticados puedan acceder a esta vista
def home(request):
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
        if 'action' in request.POST:
            action = request.POST['action']

    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'cambioperfil':
                try:
                    data['titulo'] = 'Menú principal'
                    mis_perfiles = None
                    # obtener perfiles

                    mis_perfiles = PersonaPerfil.objects.filter(status=True, persona=persona_logeado)
                    data['mis_perfiles'] = mis_perfiles
                    data['tipoperfil'] = request.GET['tipoperfil']
                    act_data_aplication(request, data)
                    tipoperfil = request.session['tipoperfil']

                    menu = AccesoModulo.objects.values_list('modulo_id').filter(status=True, activo=True,
                                                                                grupo_id=tipoperfil)
                    modulos = Modulo.objects.filter(status=True, activo=True, pk__in=menu)
                    data['persona_logeado'] = persona_logeado
                    data['modulos'] = modulos
                    return HttpResponseRedirect("/")
                except Exception as ex:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))

        else:
            try:
                data['titulo'] = 'Menú principal'
                mis_perfiles = None
                # obtener perfiles
                if not 'SUPERUSUARIO' == persona_logeado:
                    mis_perfiles = PersonaPerfil.objects.filter(status=True, persona=persona_logeado)
                    data['mis_perfiles'] = mis_perfiles

                # obtener modulos
                if usuario_logeado.is_superuser:
                    modulos = Modulo.objects.filter(status=True, activo=True)

                else:
                    menu = AccesoModulo.objects.values_list('modulo_id').filter(status=True, activo=True,
                                                                                grupo__id=tipoperfil)
                    modulos = Modulo.objects.filter(status=True, activo=True, pk__in=menu)
                data['categoriasmodulo'] = CategoriaModulo.objects.filter(status=True)
                data['tg'] = tipoperfil
                data['persona_logeado'] = persona_logeado
                data['modulos'] = modulos
                return render(request, "panel.html", data)
            except Exception as ex:
                print('Error on line {}'.format(ex.exc_info()[-1].tb_lineno))
