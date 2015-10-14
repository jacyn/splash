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

    all_projects = app_models.Project.objects.all()
    all_pages = app_models.Page.objects.all()
    all_surveys = app_models.Survey.objects.all()

    summary = dict(
        projects=dict(
            all=len(all_projects),
            published=len(all_projects.filter(live_mode=True)),
            unpublished=len(all_projects.filter(live_mode=False)),
            last_data=all_projects.order_by("-last_modified")[:1].get(),
            ),
        pages=dict(
            all=len(all_pages),
            published=len(all_pages.filter(live_mode=True)),
            unpublished=len(all_pages.filter(live_mode=False)),
            last_data=all_pages.order_by("-last_modified")[:1].get(),
            ),
        surveys=dict(
            all=len(all_surveys),
            published=len(all_surveys.filter(active=True)),
            unpublished=len(all_surveys.filter(active=False)),
            last_data=all_surveys.order_by("-last_modified")[:1].get(),
            ),
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
