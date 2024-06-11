from django import forms
from administrativo.models import PlantillaPersona, Cargo, Area, JornadaLaboral, DetalleJornadaLaboral, JornadaEmpleado, \
    DatosOrganizacion, MOTIVO_MARCACION, DatosFamiliares, Genero
from core.core import DIAS_SEMANA, PARENTESCOS

class PlantillaPersonalForm(forms.ModelForm):
    class Meta:
        model = PlantillaPersona
        fields = [
                    'persona', 'cargo', 'salario', 'fecha_ingreso', 'fecha_terminacion', 'area', 'activo'
                 ]

        error_messages = {
            'persona': {
                'unique': "Ya existe empleado registrado con este nombre. Por favor, elige a una persona diferente."
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS específicas a cada campo
        self.fields['persona'].widget.attrs.update({'class': 'form-control', 'data-live-search':'true', 'col': 'col-md-12'})
        self.fields['cargo'].widget.attrs.update({'class': 'form-control', 'data-live-search':'true', 'col': 'col-md-6'})
        self.fields['salario'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6'})
        self.fields['fecha_ingreso'].widget.attrs.update({'class': 'form-control date', 'col': 'col-md-6', 'type': 'date', 'format': 'yyyy-mm-dd'})
        self.fields['fecha_terminacion'].widget.attrs.update({'class': 'form-control date', 'col': 'col-md-6', 'type': 'date', 'format': 'yyyy-mm-dd'})
        self.fields['area'].widget.attrs.update({'class': 'form-control', 'data-live-search':'true', 'col': 'col-md-6'})
        self.fields['activo'].widget.attrs.update({'class': 'form-check-input', 'col': 'col-md-6'})

        self.fields['cargo'].queryset = Cargo.objects.filter(status=True)
        self.fields['area'].queryset = Area.objects.filter(status=True)



class JornadaForm(forms.ModelForm):
    class Meta:
        model = JornadaLaboral
        fields = [
                    'nombre'
                 ]

        error_messages = {
            'nombre': {
                'unique': "Ya existe jornada laboral registrado con este nombre."
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS específicas a cada campo
        self.fields['nombre'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-18', 'style': 'width:700px'})

class DetalleJornadaForm(forms.ModelForm):
    class Meta:
        model = DetalleJornadaLaboral
        fields = [
                    'dia', 'comienza', 'finaliza', 'motivo_entrada', 'motivo_salida'
                 ]

        error_messages = {
            'persona': {
                'unique': "Ya existe detalle en la jornada laboral registrado con este nombre."
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS específicas a cada campo
        self.fields['dia'].widget.attrs.update({'class': 'form-control', 'data-live-search':'true', 'required': 'true', 'col': 'col-md-12'})
        self.fields['motivo_entrada'].widget.attrs.update({'class': 'form-control', 'data-live-search':'true', 'required': 'true', 'col': 'col-md-6'})
        self.fields['motivo_salida'].widget.attrs.update({'class': 'form-control', 'data-live-search':'true', 'required': 'true', 'col': 'col-md-6'})
        self.fields['comienza'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6', 'required': 'true', 'type': 'text', 'placeholder': 'HH:MM'})
        self.fields['finaliza'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6', 'required': 'true', 'type': 'text', 'placeholder': 'HH:MM'})

        self.fields['dia'].queryset = DIAS_SEMANA
        self.fields['motivo_entrada'].queryset = MOTIVO_MARCACION
        self.fields['motivo_salida'].queryset = MOTIVO_MARCACION

class JornadaEmpleadoForm(forms.ModelForm):
    class Meta:
        model = JornadaEmpleado
        fields = [
                    'jornada',
                 ]

        error_messages = {
            'jornada': {
                'unique': "Ya existe detalle en la jornada laboral registrado con este nombre."
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS específicas a cada campo
        self.fields['jornada'].widget.attrs.update({'class': 'form-control', 'data-live-search':'true', 'required': 'true', 'col': 'col-md-12'})

        self.fields['jornada'].queryset = JornadaLaboral.objects.filter(status=True)


class DatosOrganizacionForm(forms.ModelForm):
    class Meta:
        model = DatosOrganizacion
        fields = [
                    'nombre', 'direccion', 'latitud', 'longitud', 'radio'
                 ]

        error_messages = {
            'persona': {
                'unique': "Ya existe detalle en la jornada laboral registrado con este nombre."
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS específicas a cada campo
        self.fields['nombre'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-12', 'required': 'true', 'type': 'text', 'placeholder': 'Nombre'})
        self.fields['direccion'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-12', 'required': 'true', 'type': 'text', 'placeholder': 'Dirección'})
        self.fields['latitud'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6', 'required': 'true', 'type': 'input', 'placeholder': 'Latitud'})
        self.fields['longitud'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6', 'required': 'true', 'type': 'input', 'placeholder': 'Longitud'})
        self.fields['radio'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6', 'required': 'true', 'type': 'input', 'placeholder': 'Radio'})

class DatosFamiliaresForm(forms.ModelForm):
    class Meta:
        model = DatosFamiliares
        fields = [
                    'parentesco', 'nombres', 'apellido1', 'apellido2', 'cedula',
                    'fecha_nacimiento', 'genero', 'correo_electronico', 'telefono',
                    'direccion'
                 ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS específicas a cada campo
        self.fields['parentesco'].widget.attrs.update({'class': 'form-control', 'data-live-search':'true', 'required': 'true', 'col': 'col-md-12'})
        self.fields['nombres'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6', 'required': 'true', 'type': 'text'})
        self.fields['apellido1'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6', 'required': 'true', 'type': 'text'})
        self.fields['apellido2'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6', 'required': 'true', 'type': 'text'})
        self.fields['cedula'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6', 'required': 'true', 'type': 'text'})
        self.fields['fecha_nacimiento'].widget.attrs.update({'class': 'form-control date', 'col': 'col-md-6', 'type': 'date', 'format': 'yyyy-mm-dd', 'required':'true'})
        self.fields['genero'].widget.attrs.update({'class': 'form-control', 'data-live-search': 'true', 'col': 'col-md-6', 'required': 'true'})
        self.fields['correo_electronico'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6'})
        self.fields['telefono'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6'})
        self.fields['direccion'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6'})

        self.fields['genero'].queryset = Genero.objects.filter(status=True)
        self.fields['parentesco'].queryset = PARENTESCOS

