# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import filer.fields.image
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0002_auto_20150606_2003'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Object',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(default=b'', max_length=255)),
                ('object_type', models.IntegerField(default=1, max_length=2, verbose_name='Object Type')),
                ('sequence', models.IntegerField(default=0)),
                ('name', models.CharField(default=b'', max_length=255, verbose_name='Object Name')),
                ('x', models.DecimalField(max_digits=30, decimal_places=25)),
                ('y', models.DecimalField(max_digits=30, decimal_places=25)),
                ('width', models.DecimalField(max_digits=30, decimal_places=25)),
                ('height', models.DecimalField(max_digits=30, decimal_places=25)),
                ('background_width', models.DecimalField(null=True, max_digits=30, decimal_places=25, blank=True)),
                ('background_height', models.DecimalField(null=True, max_digits=30, decimal_places=25, blank=True)),
                ('background_color', models.CharField(max_length=255, null=True, verbose_name='Background Color', blank=True)),
                ('background_transparency', models.IntegerField(default=100, null=True, verbose_name='Background Color Transparency', blank=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('font_color', models.CharField(max_length=255, null=True, verbose_name='Font Color', blank=True)),
                ('font_size', models.IntegerField(default=12, null=True, verbose_name='Font Size', blank=True, validators=[django.core.validators.MinValueValidator(8), django.core.validators.MaxValueValidator(48)])),
                ('text_align', models.CharField(default=b'left', max_length=64, verbose_name='Text Align', choices=[(b'left', b'Left'), (b'right', b'Right'), (b'center', b'Center')])),
                ('active', models.BooleanField(default=True)),
                ('datetime_added', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('background_image', filer.fields.image.FilerImageField(related_name='background_images', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='filer.Image', null=True)),
            ],
            options={
                'verbose_name': 'Object',
                'verbose_name_plural': 'Objects',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(default=b'', max_length=64, verbose_name='Slug')),
                ('name', models.CharField(default=b'', help_text='Name of the Page.', max_length=128, verbose_name='Name')),
                ('live_mode', models.BooleanField(default=False)),
                ('datetime_added', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('added_by', models.ForeignKey(related_name='pages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Page',
                'verbose_name_plural': 'Pages',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(default=b'', unique=True, max_length=64, verbose_name='Slug')),
                ('name', models.CharField(default=b'', help_text='Name of the Project.', max_length=128, verbose_name='Name')),
                ('description', models.CharField(max_length=512, null=True, verbose_name='Description', blank=True)),
                ('live_mode', models.BooleanField(default=False)),
                ('datetime_added', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('added_by', models.ForeignKey(related_name='projects', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(related_name='projects', verbose_name='Project Owner', to='accounting.Client')),
            ],
            options={
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, null=True, verbose_name='Title of your survey', blank=True)),
                ('thanks', models.TextField(null=True, verbose_name='Message after submission on the same page.', blank=True)),
                ('redirect_url', models.CharField(max_length=100, null=True, verbose_name='Page to be redirected after the submission.', blank=True)),
                ('submission_type', models.IntegerField(max_length=2, verbose_name='Submission Type')),
                ('sms_notification_enabled', models.BooleanField(default=False, verbose_name='Enable SMS Notification?')),
                ('sms_notification_recipient', models.CharField(max_length=64, null=True, verbose_name='SMS Notification Recipient', blank=True)),
                ('sms_notification_sender_alias', models.CharField(max_length=64, null=True, verbose_name='SMS Notification Sender Alias', blank=True)),
                ('sms_notification_message', models.CharField(max_length=256, null=True, verbose_name='SMS Notification Message', blank=True)),
                ('submit', models.CharField(default=b'Submit', max_length=30, verbose_name='Text of the Submit button.', blank=True)),
                ('active', models.BooleanField(default=True, verbose_name='Display form?')),
                ('datetime_added', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('page_object', models.OneToOneField(related_name='survey', null=True, blank=True, to='app.Object')),
            ],
            options={
                'verbose_name': 'Survey',
                'verbose_name_plural': 'Surveys',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('test_mode', models.BooleanField(default=False)),
                ('answers', models.CharField(max_length=8192, null=True, verbose_name='Answers', blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Survey Answer',
                'verbose_name_plural': 'Survey Answers',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=100, verbose_name='Question')),
                ('slug', models.SlugField(default=b'', max_length=100, verbose_name='Slug', blank=True)),
                ('field_type', models.IntegerField(max_length=100, verbose_name='Answer Type', choices=[(1, 'Single line text'), (2, 'Multi line text'), (3, 'Email'), (16, b'Mobile Number'), (13, 'Number'), (4, 'Check box'), (5, 'Check boxes'), (6, 'Drop down'), (7, 'Multi select'), (8, 'Radio buttons'), (10, 'Date'), (11, 'Date/time'), (15, 'Date of birth')])),
                ('initial', models.CharField(max_length=250, null=True, verbose_name='Initial Value', blank=True)),
                ('placeholder_text', models.CharField(max_length=100, null=True, verbose_name='Placeholder', blank=True)),
                ('choices', models.CharField(max_length=1000, verbose_name='Choices', blank=True)),
                ('required', models.BooleanField(default=True, verbose_name='Answer Required?')),
                ('default', models.CharField(max_length=2000, verbose_name='Default value', blank=True)),
                ('help_text', models.CharField(max_length=100, verbose_name='Help Message', blank=True)),
                ('active', models.BooleanField(default=True)),
                ('datetime_added', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('survey', models.ForeignKey(related_name='survey_questions', verbose_name='Survey Form', to='app.Survey')),
            ],
            options={
                'verbose_name': 'Survey Question',
                'verbose_name_plural': 'Survey Questions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revision_no', models.IntegerField()),
                ('date_revised', models.DateTimeField(auto_now_add=True)),
                ('no_of_questions', models.IntegerField(default=0)),
                ('questions', models.CharField(max_length=8192, null=True, blank=True)),
                ('survey', models.ForeignKey(related_name='revisions', verbose_name='Survey Form', to='app.Survey')),
            ],
            options={
                'verbose_name': 'Survey Revision',
                'verbose_name_plural': 'Survey Revisions',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='surveyquestion',
            unique_together=set([('survey', 'slug')]),
        ),
        migrations.AddField(
            model_name='surveyanswer',
            name='survey_revision',
            field=models.ForeignKey(related_name='answers', verbose_name='Survey Revision', to='app.SurveyRevision'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='project',
            field=models.ForeignKey(related_name='pages', verbose_name='Project Page', to='app.Project'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('project', 'slug')]),
        ),
        migrations.AddField(
            model_name='object',
            name='page',
            field=models.ForeignKey(related_name='page_objects', verbose_name='Page', to='app.Page'),
            preserve_default=True,
        ),
    ]
