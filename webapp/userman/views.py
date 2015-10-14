import json
import sys

from django.shortcuts import render, render_to_response
from django.template import RequestContext, loader as template_loader
from django.http import HttpResponseRedirect, Http404, QueryDict, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.forms import *
from django.contrib.auth.models import User, UserManager
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from userman import forms as userman_forms



@login_required
def main(request, template_name="userman/main.html"):
    context = RequestContext(request)

    if not request.user.is_staff:
        raise Http404()

    users = User.objects.filter(is_superuser=False)
    if not request.user.is_superuser and request.user.is_staff:
        users = users.exclude(is_staff=True)

    http_response = render_to_response(
        template_name, 
        {
            'users': users,
        },
        context_instance=context,
    )
    return http_response


def redirect_to_main(request):
    return HttpResponseRedirect(reverse('userman:main'))


@login_required
def read(request, user_id=None, template_name="userman/read.html"):
    context = RequestContext(request)

    if not request.user.is_staff:
        raise Http404()

    user_detail = User.objects.get(pk=user_id)

    http_response = render_to_response(
        template_name, 
        {
            'user_detail': user_detail,
        },
        context_instance=context,
    )
    return http_response


@login_required
def add(request):
    return submit(request)


@login_required
def edit(request, user_id=None):
    if user_id:
        user = User.objects.get(pk=user_id)

    return submit(request, user)


@login_required
def submit(request, user=None, template_name="userman/form.html"):
    context = RequestContext(request)

    if not request.user.is_staff:
        raise Http404()

    form = userman_forms.UserForm(user=user)
    if request.POST:
        form = userman_forms.UserForm(data=request.POST, instance=user)
        if form.is_valid():
            if user:
                user.save()
                messages.success(request, 'Updated user account "%s"' % user.username)
            else:
                user = User.objects.create_user(**form.cleaned_data)
                messages.success(request, 'Added new user account "%s"' % user.username)

            if user:
                return HttpResponseRedirect(reverse('userman:read', args=[user.pk]))

    http_response = render_to_response(
        template_name, 
        {
            'user_detail': user, 
            'form': form,
        },  
        context_instance=context,
    )   
    return http_response


@login_required
def activate(request, user_id=None):
    context = RequestContext(request)

    if not request.user.is_staff:
        raise Http404()

    user = User.objects.get(pk=user_id)
    user.is_active = True
    user.save()

    messages.success(request, 'Activated user account "%s"' % user.username)

    return HttpResponseRedirect(reverse('userman:read', args=[user.pk]))


@login_required
def deactivate(request, user_id=None):
    context = RequestContext(request)

    if not request.user.is_staff:
        raise Http404()

    user = User.objects.get(pk=user_id)
    user.is_active = False
    user.save()

    messages.success(request, 'Deactivated user account "%s"' % user.username)

    return HttpResponseRedirect(reverse('userman:read', args=[user.pk]))


@login_required
def check_username(request):
    username = request.GET.get('username')

    if not request.user.is_staff:
        raise Http404()

    if not request.is_ajax():
        messages.error(request, 'This action requires javascript (ajax).')
        return redirect_to_main(request)

    password_set = False
    try:
        user = User.objects.get(username=username, is_active=True)
        password_set = user.has_usable_password()
        exists = True
    except User.DoesNotExist:
        exists = False

    j = json.dumps({"exists": exists, "password_set": password_set})
    return HttpResponse(j, content_type="application/json", status=200)


