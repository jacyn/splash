import sys
import simplejson as json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, QueryDict, HttpResponse
from django.template import RequestContext, loader as template_loader
from django.shortcuts import render, render_to_response
from django.middleware.csrf import get_token
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt

from easy_thumbnails.files import get_thumbnailer
from filer.models import Image, File

from layout import forms as layout_forms
from layout import models as layout_models



def main(request, template_name="layout/main.html"):
    context = RequestContext(request)

    http_response = render_to_response(
        template_name, 
        {
        },
        context_instance=context,
    )
    return http_response


def redirect_to_main(request):
    return HttpResponseRedirect(reverse('layout:main'))


def objects(request):

    if not request.is_ajax():
        messages.error(request, 'This action requires javascript (ajax).')
        return redirect_to_main(request)

    layout_objects = [ obj.as_dict() for obj in layout_models.ObjectProperties.objects.filter(active=True).order_by('sequence') ]
    return HttpResponse(json.dumps(layout_objects), content_type="application/json")

def image(request):

    if not request.is_ajax():
        messages.error(request, 'This action requires javascript (ajax).')
        return redirect_to_main(request)

    filename = request.GET.get("filename", None)

    try:
        # FIXME: one only; get the latest upload
        image = File.objects.get(original_filename=filename)
    except File.DoesNotExist, e:
        image = None

    url = None
    if image is not None:
        options = {"size": (image.width, image.height), "crop": True}
        url = get_thumbnailer(image).get_thumbnail(options).url

    j = json.dumps({"url": url})
    return HttpResponse(j, content_type="application/json", status=200)


@csrf_exempt
def save(request):

    if not request.is_ajax():
        messages.error(request, 'This action requires javascript (ajax).')
        return redirect_to_main(request)

    if request.method == "POST":
        post_data = json.loads(request.POST.copy()['data'])

        for key in post_data.keys():
            data = post_data[key]

            if data["background_image"]:
                try:
                    image = File.objects.get(original_filename=data["background_image"])
                except File.DoesNotExist, e:
                    image = None
                data["background_image"] = image

            try:
                properties = layout_models.ObjectProperties.objects.get(code=data["code"])
            except layout_models.ObjectProperties.DoesNotExist, dne:
                properties = None
     
            form = layout_forms.ObjectPropertiesForm(data=data)
            if form.is_valid():
                if properties:
                    if form.cleaned_data.get('active'):
                        # existing
                        properties.name = form.cleaned_data.get('name')
                        properties.background_image = form.cleaned_data.get('background_image')
                        properties.background_color = form.cleaned_data.get('background_color')
                        properties.x = form.cleaned_data.get('x')
                        properties.y = form.cleaned_data.get('y')
                        properties.width = form.cleaned_data.get('width')
                        properties.height = form.cleaned_data.get('height')
                        properties.active = form.cleaned_data.get('active')

                        properties.save()
                    else:
                        # delete object
                        properties.delete()
                        print >> sys.stderr, "deleted object: %s" % data["code"]
                else:
                    if form.cleaned_data.get('active'):
                        # new object
                        properties = layout_models.ObjectProperties.objects.create(**form.cleaned_data)

                #messages.success(request, 'Saved "Object Properties" code "%s"' % properties.code)
                #j = json.dumps({})
                #return HttpResponse(j, content_type="application/json", status=200)

            else:
                csrf_token_value = get_token(request)
                context.update({
                    'form': form,
                    'csrf_token_value': csrf_token_value,
                });
                fragment = template_loader.render_to_string(template_name, context)
                return HttpResponse(fragment, content_type="text/html", status=400)
 
        j = json.dumps({})
        return HttpResponse(j, content_type="application/json", status=200)


  
@csrf_exempt
def properties(request, template_name="layout/form.html"):
    context = RequestContext(request)

    if not request.is_ajax():
        messages.error(request, 'This action requires javascript (ajax).')
        return redirect_to_main(request)

    data = request.POST.copy()

    image = None
    if data["background_image"]:
        try:
            image = File.objects.get(original_filename=data["background_image"])
        except File.DoesNotExist, e:
            image = None
    data["background_image"] = image

    form = layout_forms.ObjectPropertiesForm(data=data)
    context.update({
        'form': form,
    });

    fragment = template_loader.render_to_string(template_name, context)
    if form.is_valid():
        return HttpResponse(fragment, content_type="text/html", status=200)

    # invalid property details
    return HttpResponse(fragment, content_type="text/html", status=400)


def preview(request, template_name="layout/preview.html"):
    context = RequestContext(request)

    http_response = render_to_response(
        template_name, 
        {
        },
        context_instance=context,
    )
    return http_response

