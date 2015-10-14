from django.contrib import admin

from app import models as app_models


class ProjectAdmin(admin.ModelAdmin):
    list_display = [ 'owner', 'slug', 'name', 'added_by', 'datetime_added', 'last_modified' ]

admin.site.register(app_models.Project, ProjectAdmin)


class PageAdmin(admin.ModelAdmin):
    list_display = [ 'project', 'slug', 'name', 'added_by', 'datetime_added', 'last_modified' ]

admin.site.register(app_models.Page, PageAdmin)


class ObjectAdmin(admin.ModelAdmin):
    list_display = [ 'page', 'name', 'datetime_added', ]

admin.site.register(app_models.Object, ObjectAdmin)


class SurveyQuestionInline(admin.StackedInline):
    model = app_models.SurveyQuestion
    extra = 0


class SurveyRevisionInline(admin.StackedInline):
    model = app_models.SurveyRevision
    extra = 0


class SurveyAdmin(admin.ModelAdmin):
    list_display = [ 'page_object', 'title', 'submission_type', 'datetime_added', 'last_modified', ]
    inlines = [
        SurveyRevisionInline,
        SurveyQuestionInline,
    ]

admin.site.register(app_models.Survey, SurveyAdmin)


class SurveyAnswerAdmin(admin.ModelAdmin):
    list_display = [ 'survey_revision', 'answers', 'test_mode', 'date_created', ]

admin.site.register(app_models.SurveyAnswer, SurveyAnswerAdmin)
