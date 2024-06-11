# custom_context_processors.py
import datetime
from datetime import datetime, date
from core.core import TITULO_SISTEMA
from system.models import CategoriaModulo
from django.forms import model_to_dict
from django.contrib.auth.models import User, Group
from administrativo.models import PersonaPerfil, Persona, DatosOrganizacion
from system.models import AccesoModulo, Modulo
import json

def global_context(request):
    request.session['administrador_principal'] = False
    titulo_sistema = TITULO_SISTEMA
    coordenadas_configuradas = (0, 0)
    radio = 0
    organizacion = DatosOrganizacion.objects.filter(status=True)
    lista_modulos = []
    lista_grupos = []
    tipoperfil = None

    #COORDENADAS DE LA EMPRESA
    if organizacion.exists():
        organizacion = organizacion.first()
        coordenadas_configuradas = (organizacion.latitud, organizacion.longitud)
        radio = organizacion.radio


    if 'coordenadas_configuradas' in request.session:
        del request.session['coordenadas_configuradas']

    if 'radio' in request.session:
        del request.session['radio']

    request.session['coordenadas_configuradas'] = coordenadas_configuradas
    request.session['radio'] = radio

    usuario = request.user
    if usuario.id:
        persona = Persona.objects.filter(status=True, usuario=usuario)
        if persona.exists():
            persona = persona.first()
            perfil = PersonaPerfil.objects.filter(status=True, persona=persona)
            if perfil.exists():
                perfil = perfil.first()
                if perfil.is_administrador_principal == True:
                    grupo_administrativo_principal = Group.objects.filter(name='Administrativo Principal')
                    if grupo_administrativo_principal:
                        request.session['administrador_principal'] = True
                        request.session['tipoperfil'] = tipoperfil = grupo_administrativo_principal.first().id
                        lista_grupos.append(tipoperfil)
                if perfil.is_administrador == True:
                    grupo_administrativo = Group.objects.filter(name='Administrativo')
                    if grupo_administrativo:
                        request.session['tipoperfil'] = tipoperfil = grupo_administrativo.first().id
                        lista_grupos.append(tipoperfil)
                if perfil.is_empleado == True:
                    grupo_empleado = Group.objects.filter(name='Empleado')
                    if grupo_empleado:
                        request.session['tipoperfil'] = tipoperfil = grupo_empleado.first().id
                        lista_grupos.append(tipoperfil)
                if 'lista_grupos' in request.session:
                    del request.session['lista_grupos']
                request.session['lista_grupos'] = lista_grupos
                if 'perfil_principal' not in request.session:
                    request.session['perfil_principal'] = model_to_dict(perfil)
                if 'persona' not in request.session:
                    request.session['idpersona'] = persona.id


    accesos = AccesoModulo.objects.values_list('modulo_id', flat=True).filter(status=True, activo=True, grupo_id__in=lista_grupos)
    lista_modulos = Modulo.objects.filter(status=True, visible=True, pk__in=accesos).values_list('id', flat=True)
    if 'lista_modulos' in request.session:
        del request.session['lista_modulos']
    lista_modulos = [x for x in lista_modulos]
    request.session['lista_modulos'] = lista_modulos


    # Consulta las categorías del sistema
    categorias = CategoriaModulo.objects.filter(status=True,visible=True).order_by('orden')

    # Devuelve un diccionario con las variables que deseas agregar al contexto
    return {
        'titulo_sistema': titulo_sistema,
        'categorias': categorias,
        'modulos': lista_modulos,

    }
