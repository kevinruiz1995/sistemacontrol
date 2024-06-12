from django import forms
from django.contrib.auth.models import User, Group
from core.helper_form import FormBase
from system.models import CategoriaModulo, Provincia, Canton, Parroquia, Pais, Modulo
from baseapp.models import Persona

def campo_requerido(form, campo):
    form.fields[campo].widget.attrs['required'] = True


def campo_no_requerido(form, campo):
    form.fields[campo].widget.attrs['required'] = False

class CategoriaModuloForm(FormBase):
    class Meta:
        model = CategoriaModulo
        fields = ['nombre', 'descripcion', 'orden', 'visible']

        error_messages = {
            'nombre': {
                'unique': "Ya existe una categoría con este nombre. Por favor, elige un nombre diferente."
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS específicas a cada campo
        self.fields['nombre'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-12'})
        self.fields['descripcion'].widget.attrs.update({'class': 'form-control','cols':'5', 'col': 'col-md-12'})
        self.fields['orden'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6','min':0})
        self.fields['visible'].widget.attrs.update({'class': 'form-check-input', 'col': 'col-md-6'})

class ModuloForm(FormBase):
    class Meta:
        model = Modulo
        fields = ['categoria','nombre','es_modulo_padre','icono','url_name', 'orden', 'descripcion', 'activo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS específicas a cada campo
        self.fields['categoria'].widget.attrs.update({'class': 'select', 'col': 'col-md-4'})
        self.fields['nombre'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-4'})
        self.fields['es_modulo_padre'].widget.attrs.update({'class': 'form-check-input', 'col': 'col-md-4'})
        self.fields['icono'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-4'})
        self.fields['url_name'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-4'})
        self.fields['orden'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-4','min':0})
        self.fields['descripcion'].widget.attrs.update({'class': 'form-control','rows':'4', 'col': 'col-md-7'})
        self.fields['activo'].widget.attrs.update({'class': 'form-check-input', 'col': 'col-md-4'})

    def add(self):
        campo_requerido(self, 'icono')

    def editar(self):
        campo_no_requerido(self, 'icono')

class AccesoModuloForm(forms.Form):
    grupo = forms.ModelChoiceField(label="Grupo", queryset=Group.objects.all(), widget=forms.Select(attrs={'class': 'form-control', }))
    modulo = forms.ModelChoiceField(label="Módulo", queryset=Modulo.objects.filter(status=True, activo = True), widget=forms.Select(attrs={'class': 'form-control', }))
    activo = forms.BooleanField(label='Activo', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check form-switch ms-2 my-auto is-filled','checked':'checked'}))


class PaisForm(FormBase):
    class Meta:
        model = Pais
        fields = ['nombre', 'codigo_pais', 'codigo_telefono', 'codigo_idioma']

        error_messages = {
            'nombre': {
                'unique': "Ya existe un país con esta descripción. Por favor, elige una descripción diferente."
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS específicas a cada campo
        self.fields['nombre'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-12'})
        self.fields['codigo_pais'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-4'})
        self.fields['codigo_telefono'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-4'})
        self.fields['codigo_idioma'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-4'})


class ProvinciaForm(FormBase):
    class Meta:
        model = Provincia
        fields = '__all__'


class CantonForm(FormBase):
    class Meta:
        model = Canton
        fields = '__all__'


class ParroquiaForm(FormBase):
    class Meta:
        model = Parroquia
        fields = '__all__'