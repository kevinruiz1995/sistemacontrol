from django.contrib import admin

# Register your models here.
from system.models import CategoriaModulo, Modulo

admin.site.register(Modulo)
admin.site.register(CategoriaModulo)