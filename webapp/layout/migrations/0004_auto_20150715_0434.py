# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.image
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0002_auto_20150606_2003'),
        ('layout', '0003_auto_20150715_0425'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imageproperties',
            name='image',
        ),
        migrations.RemoveField(
            model_name='objectproperties',
            name='background',
        ),
        migrations.AddField(
            model_name='objectproperties',
            name='background_height',
            field=models.DecimalField(null=True, max_digits=30, decimal_places=25, blank=True),
        ),
        migrations.AddField(
            model_name='objectproperties',
            name='background_image',
            field=filer.fields.image.FilerImageField(related_name='background_image', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='filer.Image', null=True),
        ),
        migrations.AddField(
            model_name='objectproperties',
            name='background_width',
            field=models.DecimalField(null=True, max_digits=30, decimal_places=25, blank=True),
        ),
        migrations.DeleteModel(
            name='ImageProperties',
        ),
    ]
