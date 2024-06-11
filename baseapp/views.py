import datetime
from datetime import datetime, date
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from baseapp.models import Persona
from administrativo.models import PersonaPerfil, PlantillaPersona, JornadaEmpleado, DetalleRegistroEntradaSalida


@login_required # Este decorador asegura que solo los usuarios autenticados puedan acceder a esta vista
def home(request):
    try:
        data = {}
        data['request'] = request
        #DECLARACIÓN DE VARIABLES
        empleados_sin_jornadas = False
        fecha_actual = datetime.now().date()

        #CONSULTA CUÁLES SON LAS ÚLTIMAS 5 MARCACIONES QUE SE REALIZARON
        ultimas_marcaciones = DetalleRegistroEntradaSalida.objects.filter(status=True, fecha_hora__date=fecha_actual).order_by('dia__empleado').distinct('dia__empleado')[:5]

        #CONSULTA A LOS EMPLEADOS ACTIVOS Y CUÁLES DE ELLOS NO TIENEN JORNADAS LABORALES ASIGNADAS
        empleados = PlantillaPersona.objects.filter(status=True, activo=True)
        for empleado in empleados:
            jornada = JornadaEmpleado.objects.filter(status=True, empleado=empleado)
            if not jornada.exists():
                empleados_sin_jornadas = True
                break

        is_administrativo = False

        usuario = request.user
        if usuario.id:
            persona = Persona.objects.filter(status=True, usuario=usuario)
            if persona.exists():
                persona = persona.first()
                perfil = PersonaPerfil.objects.filter(status=True, persona=persona)
                if perfil.exists():
                    perfil = perfil.first()
                    if perfil.is_administrador:
                        is_administrativo = True

        # Luego, puedes pasar datos a tu template si es necesario
        context = {
            'page_titulo': 'Inicio',
            'titulo':'Inicio',
            'is_administrativo':is_administrativo,
            'empleados_sin_jornadas':empleados_sin_jornadas,
            'ultimas_marcaciones':ultimas_marcaciones,
        }

        # Renderiza el template y pasa el contexto
        return render(request, 'panel.html', context)
    except Exception as ex:
        pass
