# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0002_objectproperties_image_file2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='objectproperties',
            name='image_file',
        ),
        migrations.RemoveField(
            model_name='objectproperties',
            name='image_file2',
        ),
        migrations.RemoveField(
            model_name='objectproperties',
            name='image_height',
        ),
        migrations.RemoveField(
            model_name='objectproperties',
            name='image_width',
        ),
        migrations.AddField(
            model_name='imageproperties',
            name='height',
            field=models.DecimalField(null=True, max_digits=30, decimal_places=25, blank=True),
        ),
        migrations.AddField(
            model_name='imageproperties',
            name='width',
            field=models.DecimalField(null=True, max_digits=30, decimal_places=25, blank=True),
        ),
        migrations.AddField(
            model_name='objectproperties',
            name='background',
            field=models.ForeignKey(related_name='layout_background_image', blank=True, to='layout.ImageProperties', null=True),
        ),
    ]
