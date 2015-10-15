import sys
import simplejson as json
from datetime import datetime

from django import get_version
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, QueryDict, HttpResponse
from django.template import RequestContext, Context, loader as template_loader
from django.shortcuts import render, render_to_response
from django.middleware.csrf import get_token
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.forms.util import ErrorList

from app import forms as app_forms
from app import models as app_models
from app import reporting as app_reporting
from app import signals as app_signals
from app.logger import AppLogger

from webapp import jsonhandler


def validate(survey_id, page_object, data):
    status = dict()

    if (not survey_id) and (page_object is None):
        status.update({
            "valid": False,
            "error": [ "Missing required: survey_id and page_object" ],
        })

        return status

    survey = None
    try:
        survey = app_models.Survey.objects.get(pk=survey_id)
    except app_models.Survey.DoesNotExist, dne:
        survey = None


    form = app_forms.CustomSurveyForm(data=data, instance=survey)
    if form.is_valid():
        if (data.get("submission_type") == app_forms.SUBMISSION_TYPE.NORMAL) and (len(data.get("questions")) == 0):
            status.update({
                "valid": False,
                "error": [ "Missing required: question/s" ],
            })

            return status

        data_questions_dict = dict()
        for q in data["questions"]:
            data_questions_dict[q["slug"]] = q["label"]

        data_questions = json.dumps(data_questions_dict, sort_keys=False, default=jsonhandler.polymorphic_handler)

        revision = None
        revision_questions = None
        if survey is not None:
            # existing survey
            form.update_model_instance(survey)

            revision = survey.revisions.latest('revision_no')
            revision_questions_dict = json.loads(revision.questions)
            revision_questions = json.dumps(revision_questions_dict, sort_keys=False, default=jsonhandler.polymorphic_handler)
        else:
            # new survey
            survey = form.get_new_model(page_object=page_object)

        if not revision_questions == data_questions:
            # questions changed
            revision_data = dict(
                survey=survey,
                revision_no=1,
                no_of_questions=len(data_questions_dict),
                questions=data_questions,
            )

            if revision is not None:
                revision_no = revision.revision_no + 1
                revision_data.update({'revision_no': revision_no})

            if (data.get("submission_type") == app_forms.SUBMISSION_TYPE.FACEBOOK) and (revision is not None):
                revision = None
            else:
                revision = app_models.SurveyRevision(**revision_data)

        status.update({
            "valid": True,
            "error": None,
            "data": dict(
                survey=survey,
                revision=revision,
                questions=data.get("questions")
            ),
        })

        return status
    else:
        form_errors = json.loads(form.errors.as_json())
        errors = [ ]

        for fld in form_errors:
            for err in form_errors[fld]:
                errors.append(err.get("message"))
        
        status.update({
            "valid": False,
            "error": errors,
        })

        return status


def save_questions(survey, questions):

    for question in questions:
        field_key = question.get("slug")

        survey_question = None
        try:
            survey_question = app_models.SurveyQuestion.objects.get(survey=survey, slug=field_key)
        except app_models.SurveyQuestion.DoesNotExist, dne:
            survey_question = None

        form = app_forms.CustomSurveyQuestionForm(data=question)
        if form.is_valid():

            ### CHECK IF ACTIVE
            if survey_question is not None:
                # existing
                form.update_model_instance(survey_question)
                survey_question.save()
            else:
                # new
                survey_question = form.get_new_model(survey=survey)
                survey_question.save()

        else:
            return False

    return True


@login_required
def survey(request, template_name='survey/form.html'):
    """
    add / update survey
    """
    context = RequestContext(request)

    survey_id = request.GET.get("id", None)
    object_id = request.GET.get("object_id", None)

    try:
        survey = None
        if survey_id:
            survey = app_models.Survey.objects.get(pk=survey_id)
    except app_models.Survey.DoesNotExist, e:
        survey = None

    page_object = None
    if object_id:
        page_object = app_models.Object.objects.get(pk=object_id)
    form = app_forms.CustomSurveyForm(survey)

    if request.method == "POST":
        form = app_forms.CustomSurveyForm(data=request.POST, instance=survey)
        if form.is_valid():
            if survey:
                if form.cleaned_data.get('active'):
                    # existing
                    form.update_model_instance(survey)
                    survey.page_object = page_object
                    survey.save()
                    #messages.success(request, 'Updated survey "%s"' % survey.title)
                else:
                    # delete object
                    form.update_model_instance(survey)
                    survey.page_object = page_object
                    survey.save()
                    #messages.success(request, 'Deleted survey "%s"')
            else:
                # new survey
                survey = form.get_new_model(page_object=page_object)
                survey.save()

            j = json.dumps({"id": survey.pk})
            return HttpResponse(j, content_type="application/json", status=200)
        else:
            csrf_token_value = get_token(request)
            context.update({
                'properties': True,
                'form': form,
                'csrf_token_value': csrf_token_value,
            });
            fragment = template_loader.render_to_string(template_name, context)
            return HttpResponse(fragment, content_type="text/html", status=400)

    http_response = render_to_response(
        template_name,
        {
            'properties': True,
            'form': form,
            'survey': survey,
        },
        context_instance=context,
    )
    return http_response


@login_required
def question(request, template_name='survey/form.html'):
    """
    add / update survey question
    """
    context = RequestContext(request)

    question_id = request.GET.get("id", None)
    survey_id = request.GET.get("survey_id", None)

    try:
        survey = None
        if survey_id:
            survey = app_models.Survey.objects.get(pk=survey_id)
    except app_models.Survey.DoesNotExist, e:
        survey = None

    survey_question = None
    if survey:
        if question_id:
            survey_question = survey.survey_questions.get(pk=question_id)

    form = app_forms.CustomSurveyQuestionForm(survey_question=survey_question)
    if request.method == "POST":
        form = app_forms.CustomSurveyQuestionForm(data=request.POST, instance=survey_question)
        if form.is_valid():

            # validate uniqueness of slug
            question_exists = None
            try:
                question_exists = app_models.SurveyQuestion.objects.get(survey=survey, slug=form.cleaned_data['slug'])
                if (survey_question) and (survey_question.pk == question_exists.pk):
                   question_exists = None
            except app_models.SurveyQuestion.DoesNotExist:
                question_exists = None

            if question_exists:
                errors = form._errors.setdefault("label", ErrorList())
                errors.append(u"Question already exists")
                csrf_token_value = get_token(request)
                context.update({
                    'properties': True,
                    'form': form,
                    'csrf_token_value': csrf_token_value,
                });
                fragment = template_loader.render_to_string(template_name, context)
                return HttpResponse(fragment, content_type="text/html", status=400)

            if survey_question:
                # existing
                form.update_model_instance(survey_question)
                survey_question.save()
            else:
                # new question
                survey_question = form.get_new_model(survey=survey)
                survey_question.save()

            j = json.dumps({})
            return HttpResponse(j, content_type="application/json", status=200)
        else:
            csrf_token_value = get_token(request)
            context.update({
                'properties': True,
                'form': form,
                'csrf_token_value': csrf_token_value,
            });
            fragment = template_loader.render_to_string(template_name, context)
            return HttpResponse(fragment, content_type="text/html", status=400)

    http_response = render_to_response(
        template_name,
        {
            'properties': True,
            'form': form,
            'survey': survey,
        },
        context_instance=context,
    )
    return http_response


@csrf_exempt
def question_form(request, validate=False, template_name='survey/form.html'):
    context = RequestContext(request)

    post = request.POST.copy()

    questions = None
    form = None
    data = None
    try:
        #initial = json.loads(data)
        data = json.loads(post["data"]) 
        questions = json.loads(post["questions"]) 
        form = app_forms.CustomSurveyQuestionForm(survey_question=data)
    except Exception, e:
        data = None

    if validate:
        form = app_forms.CustomSurveyQuestionForm(data=data, questions=questions)
        if form.is_valid():
            return question_design(request, data, edit_mode=True)
        else:
            csrf_token_value = get_token(request)
            context.update({
                'form': form,
                'csrf_token_value': csrf_token_value,
            });
            fragment = template_loader.render_to_string(template_name, context)
            return HttpResponse(fragment, content_type="text/html", status=400)

    http_response = render_to_response(
        template_name,
        {
            'properties': True,
            'form': form,
            'survey': survey,
        },
        context_instance=context,
    )
    return http_response


@login_required
def properties(request, template_name='survey/properties.html'):
    """
    list survey details
    """
    context = RequestContext(request)

    survey_id = request.GET.get("id", None)
    object_code = request.GET.get("object", None)
    page_id = request.GET.get("page", None)

    page_object = None
    try:
        page_object = app_models.Object.objects.get(page__pk=page_id, code=object_code)
    except app_models.Object.DoesNotExist, dne:
        page_object = None

    try:
        survey = None
        if survey_id:
            survey = app_models.Survey.objects.get(pk=survey_id)
    except app_models.Survey.DoesNotExist, e:
        survey = None

    http_response = render_to_response(
        template_name, 
        {
            'survey': survey,
            'page_object': page_object,
            'object_code': object_code, 
        },
        context_instance=context,
    )
    return http_response


def preview(request, template_name='survey/form.html'):
    """
    view final survey
    """
    context = RequestContext(request)

    survey_id = request.GET.get("id", None)
    form = None
    try:
        survey = app_models.Survey.objects.get(pk=survey_id, active=True)
        form = app_forms.SurveyForm(survey, context)
    except app_models.Survey.DoesNotExist, dne:
        survey = None


    http_response = render_to_response(
        template_name, 
        {
            'form': form,
            'survey': survey,
        },
        context_instance=context,
    )
    return http_response


@csrf_exempt
def question_design(request, data, edit_mode=False, template_name='survey/question_design.html'):
    context = RequestContext(request)

    #if not request.is_ajax():
    #    messages.error(request, 'This action requires javascript (ajax).')
    #    return redirect_to_main(request)

    # post = request.POST.copy()

    question_slug = None
    question_form = None
    try:
        #initial = json.loads(data)
        # data = json.loads(post["data"])
        question_form = app_forms.SurveyFieldForm(data, context)
        question_slug = data["slug"]
    except Exception, e:
        question_form = None

    context.update({
        'question_slug': question_slug,
        'question_form': question_form,
        'edit_mode': edit_mode,
    });

    fragment = template_loader.render_to_string(template_name, context)
    return HttpResponse(fragment, content_type="text/html", status=200)


@csrf_exempt
def survey_design(request, template_name='survey/design.html'):
    context = RequestContext(request)

    #if not request.is_ajax():
    #    messages.error(request, 'This action requires javascript (ajax).')
    #    return redirect_to_main(request)

    post = request.POST.copy()

    edit_mode = int(request.GET.get("edit_mode", 0))
    data = dict()

    try:
        data = json.loads(post["data"])
        object_code = data["code"]
    except Exception, e:
        data = dict()

    survey_form = None
    survey = None
    if edit_mode:
        survey_form = app_forms.CustomSurveyForm(initial=data["form"])
    else:
        survey = data["form"]

    questions = [ ]
    for field in data["form"]["questions"]:
        question_form = question_design(request, field, edit_mode=edit_mode)
        questions.append(question_form)

    csrf_token_value = get_token(request)

    context.update({
        'object_code': object_code,
        'questions': questions,
        'survey_form': survey_form,
        'survey': survey,
        'csrf_token_value': csrf_token_value,
    });

    fragment = template_loader.render_to_string(template_name, context)
    return HttpResponse(fragment, content_type="text/html", status=200)


def logged(survey_revision=None, log_enabled=True, log_ext=".splashsite.survey",
            debug_log_enabled=True, debug_log_ext=".splashsite.survey.debug",
            **kwargs):

    if not survey_revision:
        return False

    app_logger = AppLogger(log_enabled=log_enabled, log_ext=log_ext, debug_log_enabled=debug_log_enabled, debug_log_ext=debug_log_ext)

    now = datetime.now().replace(microsecond=0)
    log_timestamp = now.isoformat()

    log_fields = dict(
        log_timestamp=log_timestamp,
        survey_id=survey_revision.survey.pk,
        revision_no=survey_revision.revision_no
        )
    log_fields.update(kwargs)

    log_info = u"\t".join(str(k) + ":" + str(v) for k, v in log_fields.iteritems()) + "\n"
    app_logger.log(log_info)

    return True


from app import fields
def handler(request, template_name='survey/design.html'):
    """
    submit survey details
    """
    context = RequestContext(request)

    survey_id = request.GET.get("id", None)
    test_mode = int(request.GET.get("test_mode", 0))

    try:
        survey = app_models.Survey.objects.get(pk=survey_id)
        survey_revision = survey.revisions.latest("revision_no")
    except app_models.Survey.DoesNotExist:
        survey = None

    if survey is None:
        raise Http404()
    
    if request.method == "POST":

        form = app_forms.SurveyForm(survey, context, request.POST)
        if form.is_valid():
            answers = None
            try:
                answers = json.dumps(form.cleaned_data, default=jsonhandler.polymorphic_handler)
            except Exception, e:
                answers = None

            survey_result = form.get_new_model(survey_revision=survey_revision, test_mode=test_mode, answers=answers)
            survey_result.save()

            recipient = form.cleaned_data.get(survey.sms_notification_recipient, None)

            if survey.sms_notification_enabled and recipient:
                # send sms notification via signals (only if survey has mobile number question)
                sender = None
                if survey.sms_notification_sender_alias:
                    sender = survey.sms_notification_sender_alias

                sms_notification_success = app_signals.notification_via_sms.send(sender=request.user, frm=settings.XDN_MESSAGING_API_VSHORTCODE, to=recipient, message=survey.sms_notification_message, frm_alias=sender)
                for receiver, response in sms_notification_success:
                    logged(survey_revision=survey_revision, log_ext=".splashsite.survey.sms_alert", 
                            debug_log_ext=".splashsite.survey.sms_alert.debug", **response)

            j = json.dumps({
              "thank_you_message": survey.thanks,
              "redirect_url": survey.redirect_url
            })

            # log successful survey
            if not test_mode:
                kwargs = dict(
                    success=1,
                    data=answers,
                    errors=None,
                )
                logged(survey_revision=survey_revision, **kwargs)

            return HttpResponse(j, content_type="application/json", status=200)

            # add error to form that saving failed


        ### FOR IS INVALID ###

        if not test_mode:
            kwargs = dict(
                success=0,
                errors=form.errors.as_json(),
            )
            logged(survey_revision=survey_revision, **kwargs)

        questions = [ ]
        for field in survey.questions_as_list():
            question_form = question_design(request, field, edit_mode=0)
            questions.append(question_form)


        csrf_token_value = get_token(request)
        context.update({
            'form': form,
            'object_code': survey.page_object.code,
            'questions': questions,
            'survey': survey,
            'csrf_token_value': csrf_token_value,
        });
        fragment = template_loader.render_to_string(template_name, context)
        return HttpResponse(fragment, content_type="text/html", status=400)

    j = json.dumps({})
    return HttpResponse(j, content_type="application/json", status=200)


@login_required
def reports(request, template_name='survey/reports.html'):
    context = RequestContext(request)

    all_surveys = None
    surveys = None
    pages = app_models.Page.objects.all()

    page = request.GET.get('page', 0)
    survey = request.GET.get('survey', 0)
    revision = request.GET.get('revision', 0)
    if revision:
        revision = int(revision)

    if page:
        page = int(page)
        try:
            surveys = app_models.Survey.objects.all().filter(page_object__page__pk=page)
            all_surveys = surveys
        except Exception, e:
            all_surveys = None
            surveys = None

    if survey:
        survey = int(survey)
        surveys = surveys.filter(pk=survey)

    view_context = {
        'page': page,
        'all_pages': pages,
        'survey': survey,
        'revision': revision,
        'all_surveys': all_surveys,
        'surveys': surveys,
        'export_formats': settings.EXPORT_FORMATS,
    }

    report_class = app_reporting.SurveyReport()
    if surveys:
        report_class.generate(view_context, surveys, revision)

    if ('export_to' in request.GET) and (request.GET.get('export_to') in settings.MIMETYPE_MAP) and surveys:
        filetype = request.GET.get('export_to')

        page_detail = pages.get(pk=page)
        report_filename = "[SURVEY REPORT] %s - %s's %s" % (page_detail.project.owner.name, page_detail.project.name, page_detail.name)
        export_template_name = "survey/reports_template.txt"
        export_template = "%s/%s" % (settings.TEMPLATE_DIRS, export_template_name)
        loader = template_loader.get_template(export_template_name)
        report_content = loader.render(Context(view_context))
        report_fullfilename = '%s.%s' % (report_filename, filetype)

        response_kwargs = {}
        key = 'content_type' if get_version().split('.')[1] > 6 else 'mimetype'
        response_kwargs[key] = settings.MIMETYPE_MAP.get(filetype, 'application/octet-stream')

        http_response = HttpResponse(**response_kwargs)
        http_response['Content-Disposition'] = 'attachment; filename="%s"' % report_fullfilename
        http_response.write(report_content)
    else:
        http_response = render_to_response(
            template_name, 
            view_context, 
            context_instance=context,
        )
    return http_response


@login_required
def switch_question(request, survey_id=None, question_id=None, switch=0):

    active = False
    if int(switch) == 1:
        active = True

    try:
        survey = app_models.Survey.objects.get(pk=survey_id)
        survey_question = survey.survey_questions.get(pk=question_id)
        survey_question.active = active 
        survey_question.save()

        j = json.dumps({})
        return HttpResponse(j, content_type="application/json", status=200)
    except:
        j = json.dumps({})
        return HttpResponse(j, content_type="application/json", status=500)

