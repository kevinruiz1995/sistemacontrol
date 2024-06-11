from django.http import HttpResponseRedirect, JsonResponse
from system.models import Modulo



def secure_module(f):

    def new_f(*args, **kwargs):
        request = args[0]
        if request.user.is_authenticated:
            try:
                if 'perfil_principal' in request.session:
                    return HttpResponseRedirect('/')
                    p = request.session['perfilprincipal']
                if not request.user.is_superuser:
                    return f(request)
                g = []
                app = ''
                if Modulo.objects.filter(modulogrupo_gruposid_in=g, url=request.path[1:], activo=True).exists():
                    modulo = Modulo.objects.filter(modulogrupo_gruposid_in=g, url=request.path[1:], activo=True)[0]
                    if app == 'sga' and modulo.sga:
                        return f(request)
                    if app == 'sagest' and modulo.sagest:
                        return f(request)
                    if not modulo.sagest and not modulo.sga:
                        return f(request)
                    return HttpResponseRedirect("/")
                else:
                    return HttpResponseRedirect("/")
            except Exception as ex:
                HttpResponseRedirect(f"/?info={ex}")
        else:
            HttpResponseRedirect("/")
    return new_f