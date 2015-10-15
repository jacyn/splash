import sys
import re 

from datetime import date, datetime

from django import forms
from django.core.exceptions import ValidationError
from django.template import Template
from django.template.defaultfilters import slugify
from django.conf import settings

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, ButtonHolder, Submit, Div, Button, HTML, Hidden
from crispy_forms.bootstrap import FormActions, InlineRadios, InlineCheckboxes

from app import models as app_models
from app import fields


class OBJECT_TYPE(object):
    AD = 1
    SURVEY = 2
    
class ProjectForm(forms.ModelForm):
    class Meta:
        model     = app_models.Project
        fields    = '__all__'
        exclude   = ( 'added_by', )

    helper = FormHelper()
    helper.form_tag = True
    helper.form_class = "form-horizontal style-form"

    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-10'

    helper.layout = Layout(
        Field('owner', css_class='form-control'),
        Field('name', css_class='form-control'),
        Field('slug', css_class='form-control'),
        Field('description', css_class='form-control'),
        FormActions(
            Submit('save_changes', "Save", css_class="btn btn-theme"),
            HTML("""<a class="btn btn-default" 
                      href="{% if project_detail %}{% url 'app:read_project' project_detail.pk %}{% else %}{% url 'app:projects' %}{% endif %}"
                    >Cancel</a>"""),
        ),
    )
    
    def __init__(self, project=None, *args, **kwargs):

        initial = { }
        if 'initial' in kwargs:
            initial = kwargs.get('initial')
            del kwargs['initial']

        if project:
            for fname in ProjectForm().fields.keys():
                initial[fname] = getattr(project, fname)

        super(ProjectForm, self).__init__(initial=initial, *args, **kwargs)

        
    def clean(self):
        cleaned_data = super(ProjectForm, self).clean()

        return cleaned_data

    def get_new_model(self, **kwargs):
        d = self.cleaned_data
        defaults = dict(d)
        defaults.update({
            "added_by": kwargs.get('added_by'),
        });
        return app_models.Project(**defaults)

    def update_model_instance(self, model):
        for fname in self.cleaned_data.keys():
            setattr(model, fname, self.cleaned_data.get(fname))


class PageForm(forms.ModelForm):
    class Meta:
        model     = app_models.Page
        fields    = '__all__'
        exclude   = ( 'added_by', )

    helper = FormHelper()
    helper.form_tag = True
    helper.form_class = "form-horizontal style-form"

    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-10'

    helper.layout = Layout(
        Field('project', css_class='form-control'),
        Field('name', css_class='form-control'),
        Field('slug', css_class='form-control'),
        FormActions(
            Submit('save_changes', "Save", css_class="btn btn-theme"),
            HTML("""<a class="btn btn-default" 
                      href="{% if page_detail %}{% url 'app:read_page' page_detail.pk %}{% else %}{% url 'app:pages' %}{% endif %}"
                    >Cancel</a>"""),
        ),
    )
    
    def __init__(self, page=None, *args, **kwargs):

        initial = { }
        if 'initial' in kwargs:
            initial = kwargs.get('initial')
            del kwargs['initial']

        if page:
            for fname in PageForm().fields.keys():
                initial[fname] = getattr(page, fname)

        super(PageForm, self).__init__(initial=initial, *args, **kwargs)

        
    def clean(self):
        cleaned_data = super(PageForm, self).clean()

        return cleaned_data

    def get_new_model(self, **kwargs):
        d = self.cleaned_data
        defaults = dict(d)
        defaults.update({
            "added_by": kwargs.get('added_by'),
        });
        return app_models.Page(**defaults)

    def update_model_instance(self, model):
        for fname in self.cleaned_data.keys():
            setattr(model, fname, self.cleaned_data.get(fname))


class ObjectPropertiesForm(forms.ModelForm):
    class Meta:
        model     = app_models.Object
        fields    = '__all__'
        widgets   = {
                   'background_color': forms.widgets.TextInput(attrs={'type': 'color', 'value': '#000000'}),
                   'font_color': forms.widgets.TextInput(attrs={'type': 'color', 'value': '#ffffff'}),
                   }

    helper = FormHelper()
    helper.form_tag = False

    helper.layout = Layout(
        Field('name', css_class='form-control input-sm'),
        Field('background_image', css_class='form-control input-sm'),
        Field('background_color', css_class='form-control input-sm color'),
        Field('background_transparency', css_class='form-control input-sm'),
        Field('font_color', css_class='form-control input-sm color'),
        Field('font_size', css_class='form-control input-sm'),
        Field('text_align', css_class='form-control input-sm'),
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

        return cleaned_data


    def get_new_model(self, **kwargs):
        d = self.cleaned_data
        defaults = dict(d)
        defaults.update({
            "page": kwargs.get('page'),
        });
        return app_models.Object(**defaults)

    def update_model_instance(self, model):
        for fname in self.cleaned_data.keys():
            setattr(model, fname, self.cleaned_data.get(fname))


class SurveyFieldForm(forms.Form):

    helper = FormHelper()
    helper.form_tag = False

    def __init__(self, field, context, *args, **kwargs):
        super(SurveyFieldForm, self).__init__(*args, **kwargs)

        field_key = field["slug"]
        field_type = int(field["field_type"])

        field_class = fields.CLASSES[field_type]
        field_widget = fields.WIDGETS.get(field_type)

        field_args = {"label": field["label"], "required": field["required"],
                      "help_text": field["help_text"]}

        arg_names = field_class.__init__.__code__.co_varnames
        if "choices" in arg_names:
            choices = list(fields.get_choices(field["choices"]))
            if (field_type == fields.SELECT and
                    field["default"] not in [c[0] for c in choices]):
                choices.insert(0, ("", field["placeholder_text"]))
            field_args["choices"] = choices
        if field_widget is not None:
            field_args["widget"] = field_widget

        initial_val = None
        try:
            initial_val = field["initial"]
        except KeyError:
            initial_val = Template(field["default"]).render(context)
        if initial_val:
            if field_type == fields.CHECKBOX:
                initial_val = initial_val != "False"
            self.fields[field_key] = initial_val

        self.fields[field_key] =  field_class(**field_args)

        if field_type in (fields.DOB, fields.DATE, fields.DATE_TIME):
            self.fields[field_key].widget.attrs["class"] = "default-date-picker form-control"
            if field_type == fields.DATE_TIME:
                self.fields[field_key].widget.attrs["class"] = "default-datetime-picker form-control"

            now = datetime.now()
            years = list(range(now.year, now.year - 120, -1))
            self.fields[field_key].widget.years = years

            self.fields[field_key].input_formats = settings.DATE_INPUT_FORMATS


        if field["placeholder_text"] and not field["default"]:
            text = field["placeholder_text"]
            self.fields[field_key].widget.attrs["placeholder"] = text

        if field_type not in (fields.RADIO_MULTIPLE, fields.CHECKBOX_MULTIPLE, fields.CHECKBOX, fields.DOB, fields.DATE, fields.DATE_TIME):
            self.fields[field_key].widget.attrs["class"] = "form-control input-sm"

        if field_type in (fields.SELECT_MULTIPLE, fields.SELECT):
            self.fields[field_key].widget.attrs["class"] = "question-select form-control input-sm"

        self.helper.layout = Layout( 
            Field(self.fields[field_key], css_class='form-control input-sm')
            )


class SurveyForm(forms.ModelForm):
    class Meta:
        model = app_models.Survey
        fields = '__all__'
        exclude = [ 'title', 'slug', 'submit', 'submission_type', 'thanks', 
                    'active', 'label', 'field_type', 'page_object', 'redirect_url', 
                    'sms_notification_enabled', 'sms_notification_sender_alias', 'sms_notification_recipient', 'sms_notification_message', ] # exclude

    helper = FormHelper()
    helper.form_tag = False
    helper.form_show_labels = True

    def __init__(self, form, context, *args, **kwargs):
        """
        Dynamically add each of the form fields for the given form model
        instance and its related field model instances.

        ref: https://github.com/stephenmcd/django-forms-builder/blob/master/forms_builder/forms/forms.py
        """

        self.form = form
        self.form_fields = form.survey_questions.all().filter(active=True).order_by("id")
        initial = kwargs.pop("initial", {})
        # If a FormEntry instance is given to edit, stores it's field
        # values for using as initial data.
        field_entries = {}
        if kwargs.get("instance"):
            for question in kwargs["instance"].survey_questions.all().filter(active=True).order_by("id"):
                field_entries[question.field_id] = question.value
        super(SurveyForm, self).__init__(*args, **kwargs)

        crispy_layout_fields = []
        # Create the form fields.
        for field in self.form_fields:
            field_key = field.slug
            field_class = fields.CLASSES[field.field_type]
            field_widget = fields.WIDGETS.get(field.field_type)
            field_args = {"label": field.label, "required": field.required,
                          "help_text": field.help_text}

            arg_names = field_class.__init__.__code__.co_varnames
            #if "max_length" in arg_names:
            #    field_args["max_length"] = settings.FIELD_MAX_LENGTH
            if "choices" in arg_names:
                choices = list(field.get_choices())
                if (field.field_type == fields.SELECT and
                        field.default not in [c[0] for c in choices]):
                    choices.insert(0, ("", field.placeholder_text))
                field_args["choices"] = choices
            if field_widget is not None:
                field_args["widget"] = field_widget
            #
            #   Initial value for field, in order of preference:
            #
            # - If a form model instance is given (eg we're editing a
            #   form response), then use the instance's value for the
            #   field.
            # - If the developer has provided an explicit "initial"
            #   dict, use it.
            # - The default value for the field instance as given in
            #   the admin.
            #
            initial_val = None
            try:
                initial_val = field_entries[field.id]
            except KeyError:
                try:
                    initial_val = initial[field_key]
                except KeyError:
                    initial_val = Template(field.default).render(context)
            if initial_val:
                # if field.is_a(*fields.MULTIPLE):
                #     initial_val = split_choices(initial_val)
                if field.field_type == fields.CHECKBOX:
                    initial_val = initial_val != "False"
                self.initial[field_key] = initial_val
            self.fields[field_key] = field_class(**field_args)

            if field.field_type in (fields.DOB, fields.DATE, fields.DATE_TIME):
                self.fields[field_key].widget.attrs["class"] = "default-date-picker form-control"
                if field.field_type == fields.DATE_TIME:
                    self.fields[field_key].widget.attrs["class"] = "default-datetime-picker form-control"

                now = datetime.now()
                years = list(range(now.year, now.year - 120, -1))
                self.fields[field_key].widget.years = years

                self.fields[field_key].input_formats = settings.DATE_INPUT_FORMATS


            # Add identifying CSS classes to the field.
            #css_class = field_class.__name__.lower()

            """
            if field.required:
                css_class += " required"
                if field.field_type not in (fields.CHECKBOX_MULTIPLE, fields.CHECKBOX):
                    self.fields[field_key].widget.attrs["required"] = ""
            """
            #self.fields[field_key].widget.attrs["class"] = css_class
            if field.placeholder_text and not field.default:
                text = field.placeholder_text
                self.fields[field_key].widget.attrs["placeholder"] = text

            if field.field_type not in (fields.RADIO_MULTIPLE, fields.CHECKBOX_MULTIPLE, fields.CHECKBOX, fields.DOB, fields.DATE, fields.DATE_TIME):
                self.fields[field_key].widget.attrs["class"] = "input-sm"

            if field.field_type == fields.SELECT_MULTIPLE:
                self.fields[field_key].widget.attrs["class"] = "question-select"

            crispy_layout_fields.append(
                Div(
                    Field(field_key), 
                    css_class="question-tab"
                )
            )

        crispy_layout_fields.append(
            FormActions(
                Submit('save_changes', "Submit", css_class="btn btn-theme btn-sm"),
            )
        )

        self.helper.layout = Layout(
            *crispy_layout_fields
            )


    def clean(self):
        cleaned_data = super(SurveyForm, self).clean()
        mobile_number_fields = self.form_fields.filter(field_type=fields.MOBILE_NUMBER).values_list('slug', flat=True)

        for key in mobile_number_fields:
            msisdn = self.cleaned_data.get(key, '')
            if msisdn:
                if (not msisdn.startswith('09')) and (not msisdn.startswith('639')):
                    self.add_error(key, "Mobile number must start with '09' or '639'")

                if (msisdn.startswith('09')) and (not re.match(r'^\d{11}$', msisdn)):
                    self.add_error(key, "Mobile number starts with '09' must be 11 digits")

                if (msisdn.startswith('639')) and (not re.match(r'^\d{12}$', msisdn)):
                    self.add_error(key, "Mobile number starts with '639' must be 12 digits")

                msisdn_telco = settings.FRANCHISE_LOOKUP.resolve_network(msisdn)
                msisdn_type = settings.FRANCHISE_LOOKUP.resolve_type(msisdn)
                if (not msisdn_telco) and (not msisdn_type):
                    self.add_error(key, "Invalid mobile number")

        return cleaned_data

    def get_new_model(self, **kwargs):
        defaults = dict()
        defaults.update({
            "survey_revision": kwargs.get('survey_revision', None),
            "test_mode": kwargs.get('test_mode', None),
            "answers": kwargs.get('answers', None)
        });

        return app_models.SurveyAnswer(**defaults)


from django.utils.translation import ugettext_lazy as _
class SUBMISSION_TYPE(object):

    NORMAL = 1
    FACEBOOK = 2

    CHOICES = (
        (NORMAL, _("Normal Form")),
        #(FACEBOOK, _("Facebook")),
    )


class CustomSurveyForm(forms.ModelForm):
    class Meta:
        model     = app_models.Survey
        fields    = '__all__'
        widgets = {
          'thanks': forms.Textarea(attrs={'rows':3, }),
          'sms_notification_recipient': forms.Select(),
          'sms_notification_message': forms.Textarea(attrs={'rows':3, }),
        }

    submission_type = forms.ChoiceField(widget=forms.RadioSelect(), choices=SUBMISSION_TYPE.CHOICES)

    helper = FormHelper()
    helper.form_tag = False
    helper.form_show_labels = True

    helper.layout = Layout(
        InlineRadios('submission_type', css_class='form-text-field submission_type', placeholder="Submission Type"),
        Field('title', css_class='form-control form-text-field', placeholder="Title of the Form"),
        HTML("""
              {% if survey_form.submission_type.value == 1 %}
                <div class="question-list">
                {% for question in questions %}
                  {{ question.content|safe }} 
                {% empty %}
                  <div>No question.</div>
                {% endfor %}
                </div>
                <a href="#" class="btn btn-primary btn-sm add-question"><i class="icon icon-plus"></i> Question</a>
              {% elif survey_form.submission_type.value == 2 %}
                <a class="btn btn-block btn-social btn-facebook" href="#"><span class="fa fa-facebook"></span> Sign in with Facebook</a>
              {% endif %}
             """),
        Div(
            Field('thanks', css_class='form-control form-text-field', placeholder="Thank you message after the submmission"),
            HTML("""<div><b>OR</b></div>"""),
            Field('redirect_url', css_class='form-control form-text-field', placeholder="Redirect URL after message"),
        ),
        Field('sms_notification_enabled', css_class='checkbox-custom form-text-field'),
        Field('sms_notification_recipient', css_class='form-text-field'),
        Field('sms_notification_sender_alias', css_class='form-text-field'),
        Field('sms_notification_message', css_class='form-text-field'),
    )
    
    def __init__(self, survey=None, *args, **kwargs):
        initial = { }
        if 'initial' in kwargs:
            initial = kwargs.get('initial')
            del kwargs['initial']
        if survey:
            for fname in CustomSurveyForm().fields.keys():
                initial[fname] = getattr(survey, fname)

        super(CustomSurveyForm, self).__init__(initial=initial, *args, **kwargs)

    def clean(self):
        cleaned_data = super(CustomSurveyForm, self).clean()

        thanks = cleaned_data.get('thanks', '')
        redirect_url = cleaned_data.get('redirect_url', '')
        title = cleaned_data.get('title', '')

        if (len(title) <= 0):
            self.add_error("title", "Missing required: Form Title")

        if (len(thanks) > 0) and (len(redirect_url) > 0):
            self.add_error("thanks", "Only one is allowed: Message OR Redirect URL")
        if (len(thanks) <= 0) and (len(redirect_url) <= 0):
            self.add_error("thanks", "At least one is required: Message OR Redirect URL")

        if cleaned_data.get('sms_notification_enabled'):
            recipient = cleaned_data.get('sms_notification_recipient')
            if (len(recipient) <= 0):
                self.add_error("sms_notification_recipient", "Missing required: SMS notification recipient")
            message = cleaned_data.get('sms_notification_message')
            if (len(message) <= 0):
                self.add_error("sms_notification_message", "Missing required: SMS Notification Message")

        return cleaned_data


    def get_new_model(self, **kwargs):
        d = self.cleaned_data
        defaults = dict(d)
        defaults.update({
            "page_object": kwargs.get('page_object'),
        });
        return app_models.Survey(**defaults)

    def update_model_instance(self, model):
        for fname in self.cleaned_data.keys():
            setattr(model, fname, self.cleaned_data.get(fname))



class CustomSurveyQuestionForm(forms.ModelForm):
    class Meta:
        model     = app_models.SurveyQuestion
        exclude = ('survey', 'active', )
        widgets = {
          'label': forms.Textarea(attrs={'rows': 2, }),
          'choices': forms.Textarea(attrs={'rows': 3, }),
        }

    helper = FormHelper()
    helper.form_tag = True
    # helper.help_text_inline = True
    helper.error_text_inline = True
    # helper.form_show_labels = False


    helper.layout = Layout(
        Field('label', css_class='form-control input-sm'),
        Field('placeholder_text', css_class='form-control input-sm'),
        Field('field_type', css_class='form-control input-sm'),
        Field('choices', css_class='form-control input-sm'),
        Field('required', css_class='input-sm checkbox-custom'),
        FormActions(
            Button('save_changes', 'Submit', css_class="btn btn-theme btn-sm save"),
            Button('cancel', 'Cancel', css_class="btn-default btn-sm cancel"),
        ),
    )
    
    def __init__(self, survey_question=None, questions=None, *args, **kwargs):
        initial = { }
        if 'initial' in kwargs:
            initial = kwargs.get('initial')
            del kwargs['initial']

        if survey_question:
            for fname in CustomSurveyQuestionForm().fields.keys():
                initial[fname] = survey_question.get(fname, '')

        self.questions = [ ]
        if questions:
            self.questions = questions

        super(CustomSurveyQuestionForm, self).__init__(initial=initial, *args, **kwargs)

    def clean(self):
        cleaned_data = super(CustomSurveyQuestionForm, self).clean()

        for question in self.questions:
            if cleaned_data.get("slug") != question.get("slug"):
                if cleaned_data.get("label") == question.get("label"):
                    self.add_error("label", "Question already exists")

        return cleaned_data

    def get_new_model(self, **kwargs):
        d = self.cleaned_data
        defaults = dict(d)
        defaults.update({
            "survey": kwargs.get('survey'),
        });
        return app_models.SurveyQuestion(**defaults)

    def update_model_instance(self, model):
        for fname in self.cleaned_data.keys():
            setattr(model, fname, self.cleaned_data.get(fname))

