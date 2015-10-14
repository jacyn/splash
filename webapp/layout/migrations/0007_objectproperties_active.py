# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0006_auto_20150723_0849'),
    ]

    operations = [
        migrations.AddField(
            model_name='objectproperties',
            name='active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
