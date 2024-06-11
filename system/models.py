from django.db import models
from core.helper_model import ModeloBase
from django.contrib.auth.models import User, Group
# Create your models here.

class CategoriaModulo(ModeloBase):
    nombre = models.CharField(verbose_name="Nombre", max_length=100,unique=True)
    descripcion = models.TextField(verbose_name="Descripción",max_length=300,blank=True,null=True)
    orden = models.IntegerField(default=0, verbose_name=u'Orden')
    visible = models.BooleanField(default=True, verbose_name=u'¿Está Visible?')

    class Meta:
        verbose_name = "Categoría de Módulo"
        verbose_name_plural = "Categorías de Módulos"

    def __str__(self):
        return self.nombre

    def modulos_que_son_hijos(self):
        return Modulo.objects.values_list('id',flat=True).filter(modulo_padre__isnull=False, status=True)

    def modulos(self):
        return self.modulo_set.filter(status=True, visible=True).exclude(pk__in=self.modulos_que_son_hijos()).order_by('orden')

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.strip().capitalize()
        super(CategoriaModulo, self).save(*args, **kwargs)


class Modulo(ModeloBase):
    categoria = models.ForeignKey(CategoriaModulo, on_delete=models.CASCADE, null=True, blank=True,verbose_name=f"Categoría")
    modulo_padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name=f"Módulo Padre")
    nombre = models.CharField(default='', max_length=100, verbose_name=f"Nombre", unique=True)
    icono = models.CharField(default='fe fe-clipboard', null=True, blank=True, max_length=100, verbose_name=u'Icono')
    url_name = models.CharField(default='', max_length=100, verbose_name=u'URL name',null=True, blank=True)
    descripcion = models.TextField(default='', max_length=300, verbose_name=u'Descripción', null=True, blank=True)
    orden = models.IntegerField(default=0, verbose_name=u'Orden')
    visible = models.BooleanField(default=True, verbose_name=u'¿Está Visible?')
    es_modulo_padre = models.BooleanField(default=False, verbose_name=u'¿Es módulo padre?')

    def submodulos(self):
        return Modulo.objects.filter(modulo_padre=self, status=True, visible=True).order_by('orden')

    class Meta:
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        super(Modulo, self).save(*args, **kwargs)


class AccesoModulo(ModeloBase):
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Acceso a módulo"
        verbose_name_plural = "Acceso a módulos"
        ordering = ['id']

    def __str__(self):
        return u'%s - %s - %s' % (self.grupo, self.modulo, self.activo)






class Pais(ModeloBase):
    nombre = models.CharField(max_length=100,unique=True, verbose_name='Nombre')
    codigo_pais = models.CharField(max_length=200, verbose_name='Código Pais', blank=True, null=True)
    codigo_telefono = models.CharField(max_length=10,blank=True, null=True, verbose_name='Código télefono')
    codigo_idioma = models.CharField(max_length=200, blank=True, null=True, verbose_name='Código idioma')

    class Meta:
        verbose_name = f'Pais'
        verbose_name_plural = f'Paises'

    def __str__(self):
        return f"{self.nombre}"

class Provincia(ModeloBase):
    nombre = models.CharField(max_length=100,unique=True, verbose_name="Nombre")
    codigo_provincia = models.CharField(max_length=200, verbose_name='Código provincia', blank=True, null=True)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)


    class Meta:
        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'

    def __str__(self):
        return f"{self.nombre}"

class Canton(ModeloBase):
    nombre = models.CharField(max_length=100,unique=True, verbose_name="Nombre")
    codigo = models.CharField(max_length=200, verbose_name='Código ciudad', blank=True, null=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)

    class Meta:
        verbose_name = u'Canton'
        verbose_name_plural = u'Cantones'

    def __str__(self):
        return f"{self.nombre}"

class Parroquia(ModeloBase):
    nombre = models.CharField(max_length=100,unique=True , verbose_name="Nombre")
    codigo = models.CharField(max_length=200, verbose_name='Código parroquia', blank=True, null=True)
    provincia = models.ForeignKey(Canton, on_delete=models.CASCADE)


    class Meta:
        verbose_name = u'Parroquia'
        verbose_name_plural = u'Parroquias'

    def __str__(self):
        return f"{self.nombre}"


