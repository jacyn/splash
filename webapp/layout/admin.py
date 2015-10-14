from django.contrib import admin

from layout import models as layout_models


class ObjectAdmin(admin.ModelAdmin):
    #form = select2_modelform(Product, attrs={'width': '250px'})
    list_display = [ 'name', ]

admin.site.register(layout_models.ObjectProperties, ObjectAdmin)

