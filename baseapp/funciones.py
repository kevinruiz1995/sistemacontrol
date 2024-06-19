from django.db import models
import os
from sistemacontrol import settings
from django.contrib.staticfiles import finders
from django.http import JsonResponse, HttpResponse
from sistemacontrol.settings import BASE_DIR
import datetime
from datetime import datetime
from decimal import Decimal
from django.forms import model_to_dict
from django.contrib.auth.models import User, Group
from django.template.loader import get_template
# from io import StringIO
import io as StringIO
import uuid

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    path_uri = str(BASE_DIR) + str(uri)
    result = finders.find(path_uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path

def solo_2_decimales(valor, decimales=None):
    if valor:
        if decimales:
            if decimales > 0:
                return float(Decimal(valor if valor else 0).quantize(
                    Decimal('.' + ''.zfill(decimales - 1) + '1')) if valor else 0)
            else:
                return float(Decimal(valor if valor else 0).quantize(Decimal('0')))
    return valor if valor else 0

def quitar_caracteres(cadena):
    return cadena.replace(u'ñ', u'n').replace(u'Ñ', u'N').replace(u'Á', u'A').replace(u'á', u'a').replace(u'É',u'E').replace(u'é', u'e').replace(u'Í', u'I').replace(u'í', u'i').replace(u'Ó', u'O').replace(u'ó', u'o').replace(u'Ú',u'U').replace(u'ú', u'u')

def nuevo_nombre(nombre, original):
    nombre = quitar_caracteres(nombre).lower().replace(' ', '_')
    ext = ""
    if original.find(".") > 0:
        ext = original[original.rfind("."):]
    fecha = datetime.now().date()
    hora = datetime.now().time()
    return nombre + fecha.year.__str__() + fecha.month.__str__() + fecha.day.__str__() + hora.hour.__str__() + hora.minute.__str__() + hora.second.__str__() + ext.lower()


class ModeloBase(models.Model):
    from django.contrib.auth.models import User
    usuario_creacion = models.ForeignKey(User, verbose_name='Usuario Creación', blank=True, null=True, on_delete= models.CASCADE, related_name='+', editable=False)
    fecha_creacion = models.DateTimeField(verbose_name='Fecha creación',auto_now_add=True)
    fecha_modificacion = models.DateTimeField(verbose_name='Fecha Modificación', auto_now=True)
    usuario_modificacion = models.ForeignKey(User, verbose_name='Usuario Modificación', blank=True, null=True, on_delete= models.CASCADE, related_name='+', editable=False)
    status = models.BooleanField(verbose_name="Estado del registro", default=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        usuario = None
        if len(args):
            usuario = args[0].user.id
        if self.id:
            self.usuario_modificacion_id = usuario
        else:
            self.usuario_creacion_id = usuario
        models.Model.save(self)

class ModelBaseChat(models.Model):
	id = models.UUIDField(default=uuid.uuid4, primary_key=True, db_index=True, editable=False)
	tiempo = models.DateTimeField(auto_now_add=True, blank=True, null=True)
	actualizar = models.DateTimeField(auto_now=True, blank=True, null=True)

	class Meta:
		abstract = True

def add_data_aplication(request,data):
    from system.models import Modulo
    from baseapp.models import Persona
    from administrativo.models import PersonaPerfil
    if 'lista_url_ruta' not in request.session:
        request.session['lista_url_ruta'] = [['/', 'Inicio']]
    lista_url_ruta = request.session['lista_url_ruta']

    if 'perfil_principal' not in request.session:
        mis_perfiles = PersonaPerfil.objects.filter(status=True, persona=request.user.persona_set.filter(status=True).first())
        if mis_perfiles:
            tipoperfil = mis_perfiles.first()
            if tipoperfil.is_jefe_departamental == True:
                grupo_jefe = Group.objects.filter(name='JEFE DEPARTAMENTAL')
                if grupo_jefe:
                    request.session['tipoperfil'] = grupo_jefe.first().id
            elif tipoperfil.is_administrador == True:
                grupo_administrativo = Group.objects.filter(name='ADMINISTRATIVO')
                if grupo_administrativo:
                    request.session['tipoperfil'] = grupo_administrativo.first().id
            elif tipoperfil.is_empleado == True:
                grupo_empleado = Group.objects.filter(name='EMPLEADO')
                if grupo_empleado:
                    request.session['tipoperfil'] = grupo_empleado.first().id
            request.session['perfil_principal'] = model_to_dict(mis_perfiles.first())
        # request.session.save()

    if request.method == 'GET' and request.path:
        if Modulo.objects.values("id").filter(url_name=request.path[1:],status=True).exists():
            modulo = Modulo.objects.values("url_name", "nombre").filter(status=True,url_name=request.path[1:])[0]
            ruta = ['/' + modulo['url_name'], modulo['nombre']]
            if lista_url_ruta.count(ruta) <= 0:
                if lista_url_ruta.__len__() >= 7:
                    last_ruta = lista_url_ruta[1]
                    lista_url_ruta.remove(last_ruta)
                    lista_url_ruta.append(ruta)
                else:
                    lista_url_ruta.append(ruta)
            request.session['lista_url_ruta'] = lista_url_ruta
        else:
            pass
    data["lista_url_ruta"] = lista_url_ruta
