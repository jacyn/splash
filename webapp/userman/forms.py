import sys 

from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, ButtonHolder, Submit, Div, Button, HTML, Hidden
from crispy_forms.bootstrap import FormActions

from userman import models as userman_models


class UserForm(forms.ModelForm):
    class Meta:
        model     = User
        fields    = ( 'username', 'first_name', 'last_name', 'email' )

    user_type = forms.ChoiceField(widget=forms.Select(), choices=userman_models.USER_TYPE.CHOICES, initial=userman_models.USER_TYPE.NORMAL)

    helper = FormHelper()
    helper.form_tag = True
    helper.form_class = "form-horizontal style-form"

    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-10'

    helper.layout = Layout(
        Field('username', css_class='form-control'),
        Field('user_type', css_class='form-control'),
        Field('first_name', css_class='form-control'),
        Field('last_name', css_class='form-control'),
        Field('email', css_class='form-control'),
        FormActions(
            Submit('save_changes', "Save", css_class="btn btn-theme"),
            HTML("""<a class="btn btn-default" 
                      href="{% if user_detail %}{% url 'userman:read' user_detail.pk %}{% else %}{% url 'userman:main' %}{% endif %}"
                    >Cancel</a>"""),
        ),
    )
    
    def __init__(self, user=None, *args, **kwargs):
        initial = { }
        if 'initial' in kwargs:
            initial = kwargs.get('initial')
            del kwargs['initial']
    
        if user:
            for fname in UserForm().fields.keys():
	        initial[fname] = getattr(user, fname)

        super(UserForm, self).__init__(initial=initial, *args, **kwargs)


    def get_new_model(self, **kwargs):
        d = self.cleaned_data
        defaults = dict(d)
        defaults.update({
            "is_staff": True,
        })

        del defaults["user_type"]
        return User(**defaults)

    def update_model_instance(self, model):
        for fname in self.cleaned_data.keys():
            setattr(model, fname, self.cleaned_data.get(fname))


