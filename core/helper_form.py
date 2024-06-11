from django import forms

class FormBase(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FormBase, self).__init__(*args, **kwargs)
        # Recorre los campos en el formulario
        for field_name, field in self.fields.items():
            # Verifica si el campo es un campo de selección (ChoiceField)
            if isinstance(field, forms.ChoiceField):
                # Agrega la clase CSS que desees al campo de selección
                field.widget.attrs['class'] = 'selectpicker'
                # Agrega el atributo 'data-width' con el valor '100%'
                field.widget.attrs['data-width'] = '100%'
                field.widget.attrs['data-live-search'] = "true"

    def set_required_field(self,field,required):
        self.fields[field].required = required

    def set_delete_field(self, field):
        del self.fields[field]

    def set_disabled_field(self, field,Boolean):
        self.fields[field].widget.attrs['readonly'] = Boolean
        self.fields[field].widget.attrs['disabled'] = Boolean




