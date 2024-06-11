from django.contrib import admin
from baseapp.models import Persona, Genero

# Register your models here.
admin.site.register(Genero)
admin.site.register(Persona)