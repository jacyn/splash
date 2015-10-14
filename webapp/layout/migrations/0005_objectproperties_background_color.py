# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0004_auto_20150715_0434'),
    ]

    operations = [
        migrations.AddField(
            model_name='objectproperties',
            name='background_color',
            field=models.CharField(default=b'#FFFFFF', max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
