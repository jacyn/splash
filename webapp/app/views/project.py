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

from app import forms as app_forms
from app import models as app_models
from accounting import models as accounting_models

@login_required
def main(request, template_name="project/main.html"):
    context = RequestContext(request)

    if not request.user.is_superuser:
        raise Http404()

    projects = app_models.Project.objects.all()
    all_owners = accounting_models.Client.objects.all()

    owner = 0
    if 'owner' in request.GET:
        owner_str = request.GET.get('owner', None)
        if owner_str:
            owner = int(owner_str)
        if owner:
            projects = projects.filter(owner__pk=owner)

    http_response = render_to_response(
        template_name, 
        {
            'owner': owner,
            'all_owners': all_owners,
            'projects': projects,
        },
        context_instance=context,
    )
    return http_response



def redirect_to_main(request):
    return HttpResponseRedirect(reverse('app:main'))


@login_required
def read(request, project_id=None, template_name="project/read.html"):
    context = RequestContext(request)

    if not request.user.is_superuser:
        raise Http404()

    project_detail = app_models.Project.objects.get(pk=project_id)

    http_response = render_to_response(
        template_name, 
        {
            'project_detail': project_detail,
        },
        context_instance=context,
    )
    return http_response


@login_required
def add(request):
    return submit(request)


@login_required
def edit(request, project_id=None):
    project = None
    if project_id:
        project = app_models.Project.objects.get(pk=project_id)

    return submit(request, project)


@login_required
def submit(request, project=None, template_name="project/form.html"):
    context = RequestContext(request)

    if not request.user.is_superuser:
        raise Http404()

    form = app_forms.ProjectForm(project=project)
    if request.POST:
        form = app_forms.ProjectForm(data=request.POST, instance=project)
        if form.is_valid():
            if project:
                form.update_model_instance(project)
                project.save()
                messages.success(request, 'Updated project "%s"' % project.name)
            else:
                project = form.get_new_model(added_by=request.user)
                project.save()
                messages.success(request, 'Added new project "%s"' % project.name)

            if project:
                return HttpResponseRedirect(reverse('app:read_project', args=[project.pk]))

    http_response = render_to_response(
        template_name, 
        {
            'project_detail': project, 
            'form': form,
        },  
        context_instance=context,
    )   
    return http_response


@login_required
def switch_status(request, project_id=None, switch=0):
    context = RequestContext(request)

    if not request.user.is_superuser:
        raise Http404()

    live_mode = False
    if int(switch) == 1:
        live_mode = True

    if project_id:
        project = app_models.Project.objects.get(pk=project_id)
        project.live_mode = live_mode
        project.save()

    return HttpResponseRedirect(reverse('app:read_project', args=[project.pk]))

