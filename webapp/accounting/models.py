from django.db import models
from django.utils.translation import ugettext_lazy as _


class Client(models.Model):
    name = models.CharField(
        _('Name'), max_length=128,
        null=False, blank=False, 
        default='', help_text=_("Name of the Client."))
    description = models.CharField(
        _('Description'), max_length=512,
        null=True, blank=True)
    datetime_added = models.DateTimeField(
        auto_now_add=True)
    last_modified = models.DateTimeField(
        auto_now=True)


    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.name

