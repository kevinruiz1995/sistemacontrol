from datetime import datetime

from django.db import models

from authentication.models import CustomUser
from core.core import ADMINISTRADOR_ID


class ModeloBase(models.Model):
    usuario_creacion = models.ForeignKey(CustomUser, verbose_name='Usuario Creación', blank=True, null=True, on_delete=models.CASCADE, related_name='+', editable=False)
    fecha_creacion = models.DateTimeField(verbose_name='Fecha creación', auto_now_add=True)
    fecha_modificacion = models.DateTimeField(verbose_name='Fecha Modificación', auto_now=True)
    usuario_modificacion = models.ForeignKey(CustomUser, verbose_name='Usuario Modificación', blank=True, null=True, on_delete=models.CASCADE, related_name='+', editable=False)
    status = models.BooleanField(verbose_name="Estado del registro", default=True)

    class Meta:
        abstract = True

    def eliminar_registro(self, request=None):
        self.status = False
        self.save(request)

    def save(self, *args, **kwargs):
        user= None
        if len(args):
            user = args[0].user.id
        for key, value in kwargs.items():
            if 'user_id' == key:
                user_ = value
        if self.id:
            self.usuario_modificacion_id = user if user else ADMINISTRADOR_ID
            self.fecha_modificacion = datetime.now()
        else:
            self.usuario_creacion_id = user if user else ADMINISTRADOR_ID
            self.fecha_creacion = datetime.now()
        models.Model.save(self)
