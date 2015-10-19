from django.contrib import admin

from userman import models as userman_models


class UserProfileAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'user_type', ]

admin.site.register(userman_models.UserProfile, UserProfileAdmin)

