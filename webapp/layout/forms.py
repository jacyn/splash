import sys

from django import forms
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, ButtonHolder, Submit, Div, Button, HTML, Hidden
from crispy_forms.bootstrap import FormActions

from layout import models as layout_models


class ObjectPropertiesForm(forms.ModelForm):
    class Meta:
        model     = layout_models.ObjectProperties
        fields    = '__all__'
        widgets   = {
                   'background_color': forms.widgets.TextInput(attrs={'type': 'color'}),
                   }

    helper = FormHelper()
    helper.form_tag = False

    helper.label_class = 'col-lg-3'
    helper.field_class = 'col-lg-7'

    helper.layout = Layout(
        Field('name', css_class='form-control'),
        Field('background_image'),
        Field('background_color'),
    )
    
    def __init__(self, properties=None, *args, **kwargs):
        initial = { }
        if 'initial' in kwargs:
            initial = kwargs.get('initial')
            del kwargs['initial']
        if properties:
            for fname in ObjectPropertiesForm().fields.keys():
                initial[fname] = getattr(properties, fname)

        super(ObjectPropertiesForm, self).__init__(initial=initial, *args, **kwargs)

        
    def clean(self):
        cleaned_data = super(ObjectPropertiesForm, self).clean()

        for req_field in [ 'sequence', 'code', 'name', 
                        'x', 'y', 'width', 'height'
                        ]:
            if (len(str(cleaned_data.get(req_field, ''))) == 0):
                raise ValidationError, u"Required field: %s" % req_field

        return cleaned_data

