# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0005_objectproperties_background_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objectproperties',
            name='background_color',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
