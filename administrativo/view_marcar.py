import base64
import datetime
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from baseapp.funciones import add_data_aplication
from core.utils import is_ajax
from administrativo.models import PlantillaPersona, Persona, JornadaLaboral, RegistroEntradaSalidaDiario, DetalleRegistroEntradaSalida, \
    JornadaEmpleado, DetalleJornadaLaboral
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2
from system.seguridad_sistema import control_entrada_modulos
from django.core.files.base import ContentFile
from authentication.views import comparar_rasgos

@login_required()
@control_entrada_modulos
@transaction.atomic()
def view_marcacion(request):
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
                data['titulo'] = 'Registrar marcada'
                data['titulo_tabla'] = 'Registrar marcada'
                data['persona_logeado'] = persona_logeado
                jornadaasignada = False
                idpersona = persona_logeado.id
                jornadaempleado = JornadaEmpleado.objects.filter(status=True, empleado__persona_id=idpersona)
                if jornadaempleado.exists():
                    data['jornadaempleado'] = jornadaempleado = jornadaempleado.first()
                    if jornadaempleado.empleado.coordenadamarcacion:
                        jornadaasignada = True
                fechaactual = datetime.now()
                data['jornadaasignada'] = jornadaasignada
                data['fechaactual'] = fechaactual
                return render(request, 'marcar/view.html', data)
            except Exception as ex:
                print('Error on line {}'.format(ex.exc_info()[-1].tb_lineno))

@login_required
def view_marcar(request):
    try:
        jornadaasignada = False
        idpersona = request.session['idpersona']
        jornadaempleado = JornadaEmpleado.objects.filter(status=True, empleado__persona_id=idpersona)
        if jornadaempleado.exists():
            jornadaempleado = jornadaempleado.first()
            if jornadaempleado.empleado.coordenadamarcacion:
                jornadaasignada = True
        fechaactual = datetime.now()

        context = {
            'page_titulo': "Registrar marcada",
            'titulo': "Registrar marcada",
            'jornadaasignada': jornadaasignada,
            'fechaactual': fechaactual,
        }
        return render(request, 'marcar/marcar.html', context)
    except Exception as e:
        HttpResponseRedirect(f"/?info={e.__str__()}")


@login_required
def registrar_marcada(request):
    try:
        with transaction.atomic():
            registro_marcada = False
            fechaactual = datetime.now()
            dia = fechaactual.weekday() + 1
            idpersona = request.session['idpersona']

            persona_a_marcar = Persona.objects.get(id=int(idpersona))

            if not persona_a_marcar.usuario:
                return JsonResponse({'success': False, 'errors': "No cuenta con usuario"})

            if not persona_a_marcar.usuario.imagen:
                return JsonResponse({'success': False, 'errors': "No cuentas con imagen cargada en el sistema"})

            rostro = request.POST.get('imagen', None)
            if not rostro:
                return JsonResponse({'success': False, 'errors': "Error al verificar"})

            rostro_decodificado = base64.b64decode(rostro.split(',')[1])

            imagen = ContentFile(rostro_decodificado)
            if not comparar_rasgos(imagen, persona_a_marcar.usuario.imagen):
                return JsonResponse({'success': False, 'errors': "Reconocimiento facial fallido"})

            coordenadasubicacion = request.POST['coordenadasubicacion']
            empleado = PlantillaPersona.objects.filter(status=True, activo=True, persona_id=idpersona)
            if empleado.exists():
                empleado = empleado.first()
                jornadaempleado = JornadaEmpleado.objects.filter(status=True, empleado=empleado)
                if jornadaempleado.exists():
                    jornadaempleado = jornadaempleado.first()
                    registro_diario = RegistroEntradaSalidaDiario.objects.filter(status=True, empleado=empleado, jornada=jornadaempleado.jornada, fecha_hora=fechaactual.date())
                    if not registro_diario.exists():
                        registro_diario = RegistroEntradaSalidaDiario(empleado=empleado,
                                                                      jornada=jornadaempleado.jornada,
                                                                      fecha_hora=fechaactual.date())
                        registro_diario.save(request)
                    else:
                        registro_diario = registro_diario.first()

                    detallejornada = DetalleJornadaLaboral.objects.filter(status=True, jornada=jornadaempleado.jornada)
                    if not detallejornada.exists():
                        transaction.set_rollback(True)
                        return JsonResponse({'success': False, 'errors': "La jornada laboral no cuenta con horario"})

                    detallejornada = detallejornada.filter(dia=dia).order_by('dia', 'comienza', 'finaliza')
                    if not detallejornada.exists():
                        transaction.set_rollback(True)
                        return JsonResponse({'success': False, 'errors': "Este día no cuenta como día laboral"})
                    for detalle in detallejornada:
                        registromarcada = DetalleRegistroEntradaSalida.objects.filter(status=True, dia=registro_diario, fecha_hora__date=fechaactual.date())
                        if not registromarcada.filter(motivo=detalle.motivo_entrada).exists():
                            if not detalle.motivo_entrada:
                                transaction.set_rollback(True)
                                return JsonResponse({'success': False, 'errors': "El detalle de la jornada no cuenta con motivo de marcación"})
                            nuevoregistro = DetalleRegistroEntradaSalida(dia=registro_diario,
                                                                         fecha_hora=fechaactual,
                                                                         ubicacion=coordenadasubicacion,
                                                                         motivo=detalle.motivo_entrada)
                            nuevoregistro.save(request)
                            registro_marcada = True
                            break

                        elif not registromarcada.filter(motivo=detalle.motivo_salida).exists():
                            if not detalle.motivo_salida:
                                transaction.set_rollback(True)
                                return JsonResponse({'success': False, 'errors': "El detalle de la jornada no cuenta con motivo de marcación"})
                            nuevoregistro = DetalleRegistroEntradaSalida(dia=registro_diario,
                                                                         fecha_hora=fechaactual,
                                                                         ubicacion=coordenadasubicacion,
                                                                         motivo=detalle.motivo_salida)
                            nuevoregistro.save(request)
                            registro_marcada = True
                            break

                    if not registro_marcada:
                        transaction.set_rollback(True)
                        return JsonResponse({'success': False, 'errors': "Todas las marcadas ya fueron registradas"})

                    return JsonResponse({'success': True, 'message': 'Acción realizada con éxito!'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'success': False, 'errors': "No cuenta con jornada laboral asignada"})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'success': False, 'errors': "Usted no consta como empleado"})
    except Exception as e:
        transaction.set_rollback(True)
        HttpResponseRedirect(f"/?info={e.__str__()}")


# Función para calcular la distancia haversine entre dos puntos en la Tierra
def haversine(lat1, lon1, lat2, lon2):
    try:
        # Radio de la Tierra en metros
        R = 6371000

        # Convertir las coordenadas de grados a radianes
        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)

        # Diferencias de latitud y longitud
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Calcular la distancia haversine
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distancia = R * c

        return distancia
    except Exception as ex:
        return -1


@login_required
def validarRadio(request):

    try:
        cumpleRango = False

        # Coordenadas consultadas
        coordenadas_consultadas = (float(request.GET['latitude']), float(request.GET['longitude']))  # Ejemplo de coordenadas cercanas a las configuradas

        # Calcular la distancia entre las coordenadas consultadas y las configuradas
        empleado = PlantillaPersona.objects.get(id=int(request.GET['id']))
        coordenadas_empleado = empleado.coordenadamarcacion
        distancia = haversine(coordenadas_empleado.latitud, coordenadas_empleado.longitud, coordenadas_consultadas[0],
                              coordenadas_consultadas[1])

        # Definir un radio de 50 metros
        radio = coordenadas_empleado.radio # en metros

        # Validar si la distancia es menor o igual al radio
        if float(distancia) <= float(radio):
            cumpleRango = True

        return JsonResponse({'success': True,'cumple': cumpleRango})
    except Exception as ex:
        return JsonResponse({'success': False,'cumple': cumpleRango})
