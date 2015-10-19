from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class USER_TYPE:
    ADMIN   = 1
    NORMAL  = 2

    CHOICES = [
            ( ADMIN, 'Admin' ),
            ( NORMAL, 'Normal' ),
        ]

    @classmethod
    def get_choice_label(klass, choice):
        label = None
        for i in klass.CHOICES:
            if i[0] == choice:
                label = i[1]
        return label

class UserProfile(models.Model):  
    user = models.OneToOneField(User, related_name='user_profile')
    user_type = models.IntegerField(
        _("User Type"), max_length=2,
        null=False, blank=False,
        default=USER_TYPE.NORMAL)

    def __str__(self):  
          return "%s's Profile" % self.user

    def is_admin(self):
        if self.user_type == USER_TYPE.ADMIN:
            return True
        return False

    def is_normal(self):
        if self.user_type == USER_TYPE.NORMAL:
            return True
        return False
