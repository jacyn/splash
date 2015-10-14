# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.image
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0002_auto_20150606_2003'),
        ('layout', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='objectproperties',
            name='image_file2',
            field=filer.fields.image.FilerImageField(related_name='layout_images', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='filer.Image', null=True),
        ),
    ]
