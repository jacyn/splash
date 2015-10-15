from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, QueryDict, HttpResponse
from django.template import RequestContext, loader as template_loader
from django.shortcuts import render, render_to_response

from app import models as app_models
import sys
@login_required
def main(request, template_name="dashboard/main.html"):
    context = RequestContext(request)

    projects = dict()
    try:
        all_projects = app_models.Project.objects.all()
        projects.update({
            'all': len(all_projects),
            'published': len(all_projects.filter(live_mode=True)),
            'unpublished': len(all_projects.filter(live_mode=False)),
            'last_data': all_projects.order_by("-last_modified")[:1].get(),
            })
    except app_models.Project.DoesNotExist:
        projects = dict(
            all=0,
            published=0,
            unpublished=0,
            last_data="",
            )

    pages = dict()
    try:
        all_pages = app_models.Page.objects.all()
        pages.update({
            'all': len(all_pages),
            'published': len(all_pages.filter(live_mode=True)),
            'unpublished': len(all_pages.filter(live_mode=False)),
            'last_data': all_pages.order_by("-last_modified")[:1].get(),
            })
    except app_models.Page.DoesNotExist:
        pages = dict(
            all=0,
            published=0,
            unpublished=0,
            last_data="",
            )

    surveys = dict()
    try:
        all_surveys = app_models.Survey.objects.all()
        surveys.update({
            'all': len(all_surveys),
            'published': len(all_surveys.filter(active=True)),
            'unpublished': len(all_surveys.filter(active=False)),
            'last_data': all_surveys.order_by("-last_modified")[:1].get(),
            })
    except app_models.Survey.DoesNotExist:
        surveys = dict(
            all=0,
            published=0,
            unpublished=0,
            last_data="",
            )

    summary = dict(
        projects=projects,
        pages=pages,
        surveys=surveys,
    )   

    http_response = render_to_response(
        template_name, 
        {
            'summary': summary,
        },
        context_instance=context,
    )
    return http_response

def redirect_to_main(request):
    return HttpResponseRedirect(reverse('dashboard:main'))
