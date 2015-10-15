from django import forms
from django.forms.extras import SelectDateWidget
from django.utils.translation import ugettext_lazy as _

# Constants for all available field types.
TEXT = 1
TEXTAREA = 2
EMAIL = 3
CHECKBOX = 4
CHECKBOX_MULTIPLE = 5
SELECT = 6
SELECT_MULTIPLE = 7
RADIO_MULTIPLE = 8
FILE = 9
DATE = 10
DATE_TIME = 11
HIDDEN = 12
NUMBER = 13
URL = 14
DOB = 15
MOBILE_NUMBER = 16

# Names for all available field types.
NAMES = (
    (TEXT, _("Single line text")),
    (TEXTAREA, _("Multi line text")),
    (EMAIL, _("Email")),
    (MOBILE_NUMBER, ("Mobile Number")),
    (NUMBER, _("Number")),
    #(URL, _("URL")),
    (CHECKBOX, _("Check box")),
    (CHECKBOX_MULTIPLE, _("Check boxes")),
    (SELECT, _("Drop down")),
    (SELECT_MULTIPLE, _("Multi select")),
    (RADIO_MULTIPLE, _("Radio buttons")),
    #(FILE, _("File upload")),
    (DATE, _("Date")),
    (DATE_TIME, _("Date/time")),
    (DOB, _("Date of birth")),
    #(HIDDEN, _("Hidden")),
)

# Field classes for all available field types.
CLASSES = {
    TEXT: forms.CharField,
    TEXTAREA: forms.CharField,
    EMAIL: forms.EmailField,
    CHECKBOX: forms.BooleanField,
    CHECKBOX_MULTIPLE: forms.MultipleChoiceField,
    SELECT: forms.ChoiceField,
    SELECT_MULTIPLE: forms.MultipleChoiceField,
    RADIO_MULTIPLE: forms.ChoiceField,
    FILE: forms.FileField,
    DATE: forms.DateField,
    DATE_TIME: forms.DateTimeField,
    DOB: forms.DateField,
    HIDDEN: forms.CharField,
    MOBILE_NUMBER: forms.CharField,
    NUMBER: forms.FloatField,
    URL: forms.URLField,
}

WIDGETS = {
    TEXTAREA: forms.Textarea,
    CHECKBOX_MULTIPLE: forms.CheckboxSelectMultiple,
    RADIO_MULTIPLE: forms.RadioSelect,
    DATE: SelectDateWidget,
    #DOB: SelectDateWidget,
    HIDDEN: forms.HiddenInput,
}

def get_choices(choices):
    """
    Parse a comma separated choice string into a list of choices taking
    into account quoted choices using the ``settings.CHOICES_QUOTE`` and
    ``settings.CHOICES_UNQUOTE`` settings.
    """
    choice = ""
    quoted = False
    for char in choices:
        if not quoted and char == "`":
            quoted = True
        elif quoted and char == "`":
            quoted = False
        elif char == "," and not quoted:
            choice = choice.strip()
            if choice:
                yield choice, choice
            choice = ""
        else:
            choice += char
    choice = choice.strip()
    if choice:
        yield choice, choice

