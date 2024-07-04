from authentication.models import CustomUser
from django.db import models
from core.helper_model import ModeloBase



CHOICE_GENER0 = (
    (1, u'Masculino'),
    (2, u'Femenino'),
)

class Genero(ModeloBase):
    nombre = models.CharField(max_length=100, verbose_name=u'Género')

    class Meta:
        verbose_name = "Género"
        verbose_name_plural = "Géneros"
        ordering = ['id']

    def __str__(self):
        return u'%s' % self.nombre

class Persona(ModeloBase):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    nombres = models.CharField(max_length=700, blank=True, null=True, verbose_name=u"Nombres")
    apellido1 = models.CharField(max_length=700, blank=True, null=True, verbose_name=u"Primer apellido")
    apellido2 = models.CharField(max_length=700, blank=True, null=True, verbose_name=u"Segundo apellido")
    nombres_compleo= models.CharField(max_length=1000, blank=True, null=True, verbose_name=u"Nombres completos")
    cedula = models.CharField(max_length=20, verbose_name=u"Cédula", blank=True, null=True, db_index=True)
    pasaporte = models.CharField(default='', max_length=20, blank=True, null=True, verbose_name=u"Pasaporte", db_index=True)
    ruc = models.CharField(default='', max_length=20, blank=True, null=True, verbose_name=u"Ruc", db_index=True)
    direccion = models.CharField(default='', max_length=1000, blank=True, null=True, verbose_name=u"Dirección", db_index=True)
    genero = models.ForeignKey(Genero, blank=True, null=True, on_delete=models.CASCADE, verbose_name=u"Género")
    fecha_nacimiento = models.DateField(verbose_name=u"Fecha nacimiento", blank=True, null=True)
    correo_electronico = models.EmailField(verbose_name=u"Email", blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name=u"Teléfono")
    foto = models.FileField(upload_to='fotopersona/', blank=True, null=True, verbose_name='Foto de la persona')


    class Meta:
        verbose_name = u'Persona'
        verbose_name_plural = u'Personas'

    def calculate_username(self, variant=1):
        persona = self
        alfabeto = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                    'u',
                    'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        s = persona.nombres.lower().split(' ')
        while '' in s:
            s.remove('')
        if persona.apellido2:
            usernamevariant = s[0][0] + persona.apellido1.lower() + persona.apellido2.lower()[0]
        else:
            usernamevariant = s[0][0] + persona.apellido1.lower()
        usernamevariant = usernamevariant.replace(' ', '').replace(u'ñ', 'n').replace(u'á', 'a').replace(u'é',
                                                                                                         'e').replace(
            u'í', 'i').replace(u'ó', 'o').replace(u'ú', 'u')
        usernamevariantfinal = ''
        for letra in usernamevariant:
            if letra in alfabeto:
                usernamevariantfinal += letra
        if variant > 1:
            usernamevariantfinal += str(variant)
        if not CustomUser.objects.filter(username=usernamevariantfinal).exclude(persona=persona).exists():
            return usernamevariantfinal
        else:
            return calculate_username(self, variant + 1)

    def __str__(self):
        return f"{self.nombres} {self.apellido1} {self.apellido2}"

    def get_card_id(self):
        if self.cedula:
            return self.cedula
        elif self.pasaporte:
            return self.pasaporte
        elif self.ruc:
            return self.ruc

    def is_jefe_departamental(self):
        return self.personaperfil_set.filter(status=True, is_jefe_departamental=True).exists()

    def perfil_administrativo(self):
        return self.personaperfil_set.filter(status=True, is_administrador=True).exists()

    def perfil_empleado(self):
        return self.personaperfil_set.filter(status=True, is_empleado=True).exists()

    def persona_es_empleado(self):
        return self.plantillapersona_set.filter(status=True, activo=True)
