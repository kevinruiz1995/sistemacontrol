from django import forms
from core.helper_form import FormBase
from baseapp.models import Persona, Genero

class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = [
                    'nombres', 'apellido1', 'apellido2', 'cedula', 'pasaporte', 'ruc', 'genero',
                    'fecha_nacimiento', 'direccion', 'correo_electronico', 'telefono', 'foto'
                 ]

        error_messages = {
            'persona': {
                'unique': "Ya existe persona registrada con este nombre."
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS específicas a cada campo
        self.fields['nombres'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-12', 'required':'true'})
        self.fields['apellido1'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6', 'required':'true'})
        self.fields['apellido2'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6', 'required':'true'})
        self.fields['cedula'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-4'})
        self.fields['pasaporte'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-4'})
        self.fields['ruc'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-4'})
        self.fields['direccion'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-12', 'required':'true'})
        self.fields['genero'].widget.attrs.update({'class': 'form-control', 'data-live-search':'true', 'col': 'col-md-6', 'required':'true'})
        self.fields['fecha_nacimiento'].widget.attrs.update({'class': 'form-control date', 'col': 'col-md-6', 'type': 'date', 'format': 'yyyy-mm-dd', 'required':'true'})
        self.fields['correo_electronico'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6'})
        self.fields['telefono'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-6'})
        self.fields['foto'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-12'})

        self.fields['genero'].queryset = Genero.objects.filter(status=True)


    def bloquear_cedula(self):
        self.fields['cedula'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-12', 'required': 'False', 'readonly': 'true'})
        self.fields['pasaporte'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-12', 'required': 'False', 'readonly': 'true'})
        self.fields['ruc'].widget.attrs.update({'class': 'form-control', 'col': 'col-md-12', 'required': 'False', 'readonly': 'true'})