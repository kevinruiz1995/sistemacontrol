from django.db import models
from core.helper_model import ModeloBase
from core.core import IDENTIFICACIONES
from baseapp.models import Persona, Genero
from core.core import DIAS_SEMANA, PARENTESCOS

class DatosOrganizacion(ModeloBase):
    nombre = models.CharField(blank=True, null=True, max_length=500, verbose_name=u"Nombre de la empresa")
    direccion = models.CharField(blank=True, null=True, max_length=500, verbose_name=u"Dirección de la empresa")
    latitud = models.FloatField(default=0, blank=True, null=True, verbose_name="Latitud")
    longitud = models.FloatField(default=0, blank=True, null=True, verbose_name="Longitud")
    radio = models.FloatField(default=0, blank=True, null=True, verbose_name="Radio disponible para marcar")

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['id']

    def __str__(self):
        return f"{self.nombre}"

class PersonaPerfil(ModeloBase):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, blank=True, null=True)
    is_jefe_departamental = models.BooleanField(default=False, verbose_name=u'Es jefe departamental?')
    is_administrador = models.BooleanField(default=False, verbose_name=u'Es administrador?')
    is_empleado = models.BooleanField(default=False, verbose_name=u'Es empleado?')

    class Meta:
        verbose_name = "Perfil de persona"
        verbose_name_plural = "Perfiles de personas"
        ordering = ['id']

    def nombre_persona(self):
        return self.persona.__str__()

    def __str__(self):
        if self.es_administrador() and self.es_empleado():
            return u'%s - %s' % (self.nombre_persona(), "ADMINISTRADOR - EMPLEADO")
        elif not self.es_administrador() and self.es_empleado():
            return u'%s - %s' % (self.nombre_persona(), "EMPLEADO")
        elif self.es_administrador() and not self.es_empleado():
            return u'%s - %s' % (self.nombre_persona(), "ADMINISTRADOR")
        else:
            return u'%s' % "NO TIENE PERFIL"

    def es_empleado(self):
        return self.is_empleado

    def es_administrador(self):
        return self.is_administrador


class DatosFamiliares(ModeloBase):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, blank=True, null=True)
    parentesco = models.IntegerField(choices=PARENTESCOS, verbose_name='Parentesco', blank=True, null=True)
    nombres = models.CharField(max_length=700, blank=True, null=True, verbose_name=u"Nombres")
    apellido1 = models.CharField(max_length=700, blank=True, null=True, verbose_name=u"Primer apellido")
    apellido2 = models.CharField(max_length=700, blank=True, null=True, verbose_name=u"Segundo apellido")
    cedula = models.CharField(max_length=20, verbose_name=u"Cédula", blank=True, null=True, db_index=True)
    fecha_nacimiento = models.DateField(verbose_name=u"Fecha nacimiento", blank=True, null=True)
    genero = models.ForeignKey(Genero, blank=True, null=True, on_delete=models.CASCADE, verbose_name=u"Género")
    correo_electronico = models.EmailField(verbose_name=u"Email", blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name=u"Teléfono")
    direccion = models.CharField(default='', max_length=1000, blank=True, null=True, verbose_name=u"Dirección", db_index=True)


    def __str__(self):
        return f"{self.nombres} {self.apellido1} {self.apellido2}"

    class Meta:
        verbose_name = 'Datos del familiar'
        verbose_name_plural = 'Datos familiares'



class Cargo(ModeloBase):
    nombre = models.CharField(blank=True, null=True, max_length=300, verbose_name=u"Nombre del cargo")

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.strip().capitalize()
        super(Cargo, self).save(*args, **kwargs)


class Area(ModeloBase):
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Área u oficinas')
    encargado = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='+', blank=True, null=True, verbose_name=u'Persona encargada del área')

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        verbose_name = 'Área de la empresa'
        verbose_name_plural = 'Áreas de la empresa'

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.strip().capitalize()
        super(Area, self).save(*args, **kwargs)

#MODELO PARA CONFIGURAR LAS COORDENADAS
class ConfiguracionCoordenadaMarcacion(ModeloBase):
    nombre = models.CharField(blank=True, null=True, max_length=500, verbose_name=u"Nombre")
    latitud = models.FloatField(default=0, blank=True, null=True, verbose_name="Latitud")
    longitud = models.FloatField(default=0, blank=True, null=True, verbose_name="Longitud")
    radio = models.FloatField(default=0, blank=True, null=True, verbose_name="Radio disponible para marcar")

    class Meta:
        verbose_name = 'Coordenada para marcar'
        verbose_name_plural = 'Coordenadas para las marcaciones'

    def __str__(self):
        return f"{self.nombre} {self.latitud}, {self.longitud}"

#REGISTRO PERSONAL DE LA EMPRESA
class PlantillaPersona(ModeloBase):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Persona")
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Cargo")
    coordenadamarcacion = models.ForeignKey(ConfiguracionCoordenadaMarcacion, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Coordenada disponible para marcar")
    salario = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True, verbose_name="Salario")
    fecha_ingreso = models.DateField(blank=True, null=True, verbose_name="Fecha de inicio del contrato")
    fecha_terminacion = models.DateField(blank=True, null=True, verbose_name="Fecha de terminación del contrato")
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Área")
    activo = models.BooleanField(default=False, verbose_name="Persona trabaja actualmente?")

    def __str__(self):
        return f"{self.persona.__str__()} - Cargo: {self.cargo if self.cargo else 'Sin asignar'}"

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'


    def total_marcadas(self):
        registro_diario = RegistroEntradaSalidaDiario.objects.filter(status=True, empleado=self).values_list('id', flat=True)
        total_marcadas = DetalleRegistroEntradaSalida.objects.filter(status=True, dia_id__in=registro_diario).count()
        return total_marcadas


class JornadaLaboral(ModeloBase):
    nombre = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre}"

    def detalle(self, dia):
        detalle_ = self.detallejornadalaboral_set.filter(status=True, dia=dia)
        if detalle_.exists():
            return detalle_
        return None

MOTIVO_MARCACION = (
    (1, 'Entrada'),
    (2, 'Salida almuerzo'),
    (3, 'Entrada almuerzo'),
    (4, 'Salida'),
)

class DetalleJornadaLaboral(ModeloBase):
    jornada = models.ForeignKey(JornadaLaboral, on_delete=models.CASCADE, null=True, blank=True)
    dia = models.IntegerField(choices=DIAS_SEMANA, verbose_name='Día de la semana', blank=True, null=True)
    comienza = models.TimeField(blank=True, null=True, verbose_name=u'Hora que inicia la jornada')
    finaliza = models.TimeField(blank=True, null=True, verbose_name=u'Hora que finaliza la jornada')
    motivo_entrada = models.IntegerField(choices=MOTIVO_MARCACION, verbose_name='Motivo', blank=True, null=True)
    motivo_salida = models.IntegerField(choices=MOTIVO_MARCACION, verbose_name='Motivo', blank=True, null=True)

    def __str__(self):
        return f"{self.get_dia_display()}"

    def rango_fecha(self):
        return f"{self.comienza} - {self.finaliza}"


class JornadaEmpleado(ModeloBase):
    empleado = models.ForeignKey(PlantillaPersona, on_delete=models.CASCADE, null=True, blank=True)
    jornada = models.ForeignKey(JornadaLaboral, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.jornada}"


#MARCAR
class RegistroEntradaSalidaDiario(ModeloBase):
    empleado = models.ForeignKey(PlantillaPersona, on_delete=models.CASCADE, null=True, blank=True, related_name='registromarcadaempleado')
    jornada = models.ForeignKey(JornadaLaboral, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Jornada del empleado')
    fecha_hora = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Jornada: {self.jornada.__str__()} - Fecha: {self.fecha_hora}"

    def mismarcaciones(self, motivo):
        return self.detalleregistroentradasalida_set.filter(status=True, motivo=motivo)

class DetalleRegistroEntradaSalida(ModeloBase):
    dia = models.ForeignKey(RegistroEntradaSalidaDiario, on_delete=models.CASCADE, null=True, blank=True)
    fecha_hora = models.DateTimeField(null=True, blank=True)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    motivo = models.IntegerField(choices=MOTIVO_MARCACION, verbose_name='Numeración para marcar', blank=True, null=True)



#ANTICIPO DE SALARIO QUE REALIZAN LOS EMPLEADOS
class PrestamoSalario(ModeloBase):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Persona")
    salario = models.FloatField(default=0, blank=True, null=True, verbose_name="Salario del empleado")
    monto = models.FloatField(default=0, blank=True, null=True, verbose_name="Monto del préstamo")
    monto_libre = models.FloatField(default=0, blank=True, null=True, verbose_name="Monto libre")
    cotizacion_porcentaje_dic = models.FloatField(default=30, blank=True, null=True, verbose_name="Porcentaje diciembre")
    cotizacion_dic = models.FloatField(default=0, blank=True, null=True, verbose_name="Cotización diciembre")
    cantidad_cuotas = models.IntegerField(default=0, blank=True, null=True, verbose_name='Cantidad de cuotas')
    motivo = models.CharField(max_length=250, verbose_name="Observación")

    class Meta:
        verbose_name = 'Préstamo salario'
        verbose_name_plural = 'Préstamos del salario'

    def __str__(self):
        return f"Empleado: {self.persona.__str__()}, monto: {self.monto}"

class AmortizacionPrestamo(ModeloBase):
    prestamo = models.ForeignKey(PrestamoSalario, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Préstamo")
    anio = models.IntegerField(blank=True, null=True, verbose_name=f"Año")
    mes = models.IntegerField(blank=True, null=True, verbose_name=f"Mes")
    monto_inicial_mes = models.FloatField(default=0, blank=True, null=True, verbose_name=f"Monto inicial")
    monto_final_mes = models.FloatField(default=0, blank=True, null=True, verbose_name=f"Monto final")
    monto_real = models.FloatField(default=0, blank=True, null=True, verbose_name=f"Monto a cancelar")

    class Meta:
        verbose_name = 'Amortización de préstamo'
        verbose_name_plural = 'Amortizaciones de préstamos'

    def __str__(self):
        return f"Préstamos: {self.prestamo.__str__()}, monto a cancelar: {self.monto_real}"
