from django import template

register = template.Library()

@register.simple_tag
def filtro(lista, filtro):
    if "__callArg" not in lista.__dict__:
        lista.__callArg = []
    lista.__callArg.append(filtro)
    return lista

@register.simple_tag
def funcion(lista, metodo):
    method = getattr(lista, metodo)
    if "__callArg" in lista.__dict__:
        ret = method(*lista.__callArg)
        del lista.__callArg
        return ret
    return method()

@register.simple_tag
def cifrar(texto):
    clave = 10  # Valor fijo para el cifrado
    texto_cifrado = ""
    for caracter in str(texto):
        nuevo_caracter = chr(ord(caracter) + clave)
        texto_cifrado += nuevo_caracter
    return texto_cifrado

@register.simple_tag
def descifrar(texto_cifrado):
    clave = 10  # Valor fijo para el cifrado (debe ser el mismo que se utilizó para cifrar)
    texto_descifrado = ""
    for caracter in texto_cifrado:
        original_caracter = chr(ord(caracter) - clave)
        texto_descifrado += original_caracter
    return texto_descifrado



register.filter("cifrar", cifrar)
register.filter("descifrar", descifrar)
register.filter("filtro", filtro)
register.filter("funcion", funcion)