from django.urls import path

from administrativo import view_plantillapersonal, view_prestamosalario, views, view_marcar
from administrativo.view_personas import listar_personas, crear_persona, editar_persona, eliminar_persona, activar_desactivar_perfil
from administrativo.view_jornada import view
from administrativo.view_marcar import validarRadio, registrar_marcada
from administrativo.view_jornadaempleado import listar_jornadaempleado, crear_jornadaempleado, consultarempleados, editar_jornadaempleado, \
    eliminar_jornadaempleado
from administrativo.organizacion import editar_organizacion
from administrativo.view_mismarcaciones import listar_mismarcaciones
from administrativo.view_marcacionesempleados import listar_personasmarcaciones, listar_marcacionesempleado
from administrativo.view_mibiografia import mibiografia, datos_familiares, crear_datosfamiliares, editar_datosfamiliares, \
    eliminar_datosfamiliares, editar_mibiografia, mis_marcadas
from administrativo.conf_acceso_modulo import view_acceso_modulo
from administrativo.conf_grupo import view_grupo
from administrativo.view_modulo import view_modulo

app_name = 'administrativo'
urlpatterns = [
    #URLS CATEGORÍA ADMINISTRATIVO

    #CONFIGURACIÓN SISTEMA
    path(r'conf_sistemas/grupos/', view_grupo, name='conf_grupo'),
    path(r'conf_sistemas/modulos/', view_modulo, name='conf_modulo'),
    path(r'conf_sistemas/acceso_modulos/', view_acceso_modulo, name='conf_acceso_modulo'),

    #CONSULTAS AUTOEJECUTABLES
    path('/consultaAdministrativos/', views.consultaAdministrativos, name='consultaAdministrativos'),
    path('/consultaEmpleados/', views.consultaEmpleados, name='consultaEmpleados'),
    path('/consultaPersonas/', views.consultaPersonas, name='consultaPersonas'),
    path('/consultaMarcadas/', views.consultaMarcadas, name='consultaMarcadas'),

    #MÓDULO ORGANIZACIÓN
    path('editar_organizacion/', editar_organizacion, name='editar_organizacion'),

    #MÓDULO PERSONAS
    path('personas/', listar_personas, name='listar_personas'),
    path('personas/add', crear_persona, name='crear_persona'),
    path('personas/eliminar/<int:pk>/', eliminar_persona, name='eliminar_persona'),
    path('personas/editar/<int:pk>/', editar_persona, name='editar_persona'),
    path('personas/activar_desactivar_perfil/', activar_desactivar_perfil, name='activar_desactivar_perfil'),

    #MÓDULO PLANTILLA PERSONAL
    path('personal/', view_plantillapersonal.listar_personal, name='listar_personal'),
    path('personal/add', view_plantillapersonal.crear_personal, name='crear_personal'),
    path('personal/eliminar/<int:pk>/', view_plantillapersonal.eliminar_personal, name='eliminar_personal'),
    path('personal/editar/<int:pk>/', view_plantillapersonal.editar_personal, name='editar_personal'),
    path('personal/actualizar_estado/', view_plantillapersonal.actualizar_estado, name='actualizar_estado'),

    #MÓDULO PRÉSTAMO SALARIO
    path('prestamo/', view_prestamosalario.listar_personal, name='listar_personales'),
    path('prestamo/prestamos', view_prestamosalario.listar_prestamos_empleado, name='listar_prestamos_empleado'),
    path('prestamo/prestamos/add', view_prestamosalario.solicitar_prestamo, name='solicitar_prestamo'),
    path('prestamo/eliminar/<int:pk>/', view_plantillapersonal.eliminar_personal, name='eliminar_personal'),
    path('prestamo/editar/<int:pk>/', view_plantillapersonal.editar_personal, name='editar_personal'),
    path('prestamo/actualizar_estado/', view_plantillapersonal.actualizar_estado, name='actualizar_estado'),

    #MÓDULO MARCAR
    path('marcar/', view_marcar.view_marcar, name='view_marcar'),
    path('validarRadio/', validarRadio, name='validarRadio'),
    path('registrar_marcada/', registrar_marcada, name='registrar_marcada'),

    #MÓDULO JORNADA
    path('jornadas/', view, name='jornadas'),

    #MÓDULO JORNADA EMPLEADO
    path('jornadasempleado/', listar_jornadaempleado, name='listar_jornadaempleado'),
    path('jornadasempleado/add', crear_jornadaempleado, name='crear_jornadaempleado'),
    path('jornadasempleado/editar/<int:pk>/', editar_jornadaempleado, name='editar_jornadaempleado'),
    path('jornadasempleado/eliminar/<int:pk>/', eliminar_jornadaempleado, name='eliminar_jornadaempleado'),
    path('/consultarempleados/', consultarempleados, name='consultarempleados'),

    #MÓDULO MIS MARCACIONES
    path('mismarcaciones/', listar_mismarcaciones, name='listar_mismarcaciones'),

    #MÓDULO MARCACIONES DE EMPLEADOS
    path('marcadasempleado/', listar_personasmarcaciones, name='listar_personasmarcaciones'),
    path('marcacionesempleado/<int:id>/', listar_marcacionesempleado, name='listar_marcacionesempleado'),

    #MÓDULO MI BIOGRAFÍA
    path('mibiografia/', mibiografia, name='mibiografia'),
    path('mibiografia/editar/', editar_mibiografia, name='editar_mibiografia'),
    path('datos_familiares/', datos_familiares, name='datos_familiares'),
    path('datosfamiliares/add', crear_datosfamiliares, name='crear_datosfamiliares'),
    path('datosfamiliares/editar/<int:id>/', editar_datosfamiliares, name='editar_datosfamiliares'),
    path('datosfamiliares/eliminar/<int:id>/', eliminar_datosfamiliares, name='eliminar_datosfamiliares'),
    path('mis_marcadas/', mis_marcadas, name='mis_marcadas'),

]
