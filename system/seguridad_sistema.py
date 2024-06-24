from django.http import HttpResponseRedirect, JsonResponse
from system.models import AccesoModulo, Modulo



def control_entrada_modulos(f):
    def new_f(*args, **kwargs):
        request = args[0]
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return f(request)
            if 'tipoperfil' in request.session:
                tipogrupo = request.session['tipoperfil']
                menu = AccesoModulo.objects.values_list('modulo_id').filter(status=True, activo=True, grupo__id=tipogrupo)
                modulos = Modulo.objects.filter(status=True, activo=True, pk__in=menu, url_name=request.path[1:])
                if modulos.exists():
                    return f(request)
                else:
                    return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/')
    return new_f