from django.contrib import admin

from accounting import models as accounting_models


class ClientAdmin(admin.ModelAdmin):
    list_display = [ 'name', ]

admin.site.register(accounting_models.Client, ClientAdmin)
