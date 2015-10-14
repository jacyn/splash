from django.contrib.auth.models import User
#import advantage.iam
import sys

class CustomUserBackend(object):

    def authenticate(self, username=None, password=None):

        print >> sys.stderr, "starting to authenticate.. " 
        try:
            user = User.objects.get(username=username)
        except User.objects.DoesNotExists:
            user = None
        
        if user is not None and not user.password:
            print >> sys.stderr, "%s" % user.password
        login_valid = True
        #login_valid = advantage.iam.login(username, password)

        if login_valid:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User(username=username, password='')
                user.is_staff = False
                user.is_superuser = False
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
