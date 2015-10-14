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


@login_required
def main(request, template_name="page/main.html"):
    context = RequestContext(request)

    projects = app_models.Project.objects.all()
    pages = app_models.Page.objects.all()

    project = 0
    if 'project' in request.GET:
        project_str = request.GET.get('project', None)
        if project_str:
            project = int(project_str)
        if project:
            pages = pages.filter(project__pk=project)

    http_response = render_to_response(
        template_name, 
        {
            'project': project,
            'all_projects': projects,
            'pages': pages,
        },
        context_instance=context,
    )
    return http_response


def redirect_to_main(request):
    return HttpResponseRedirect(reverse('app:main'))


@login_required
def read(request, page_id=None, template_name="page/read.html"):
    context = RequestContext(request)

    page_detail = app_models.Page.objects.get(pk=page_id)

    http_response = render_to_response(
        template_name, 
        {
            'page_detail': page_detail,
        },
        context_instance=context,
    )
    return http_response


@login_required
def add(request):
    return submit(request)


@login_required
def edit(request, page_id=None):
    page = None
    if page_id:
        page = app_models.Page.objects.get(pk=page_id)

    return submit(request, page)


@login_required
def submit(request, page=None, template_name="page/form.html"):
    context = RequestContext(request)

    if not request.user.is_superuser:
        raise Http404()

    form = app_forms.PageForm(page=page)
    if request.POST:
        form = app_forms.PageForm(data=request.POST, instance=page)
        if form.is_valid():
            if page:
                form.update_model_instance(page)
                page.save()
                messages.success(request, 'Updated page "%s"' % page.name)
            else:
                page = form.get_new_model(added_by=request.user)
                page.save()
                messages.success(request, 'Added new page "%s"' % page.name)

            if page:
                return HttpResponseRedirect(reverse('app:read_page', args=[page.pk]))

    http_response = render_to_response(
        template_name, 
        {
            'page_detail': page, 
            'form': form,
        },  
        context_instance=context,
    )   
    return http_response


@login_required
def switch_status(request, page_id=None, switch=0):
    context = RequestContext(request)

    live_mode = False
    if int(switch) == 1:
        live_mode = True

    if page_id:
        page = app_models.Page.objects.get(pk=page_id)
        page.live_mode = live_mode
        page.save()

    return HttpResponseRedirect(reverse('app:read_page', args=[page.pk]))

