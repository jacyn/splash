# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.image
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0002_auto_20150606_2003'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageProperties',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', filer.fields.image.FilerImageField(related_name='object_image', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='filer.Image', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ObjectProperties',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(default=b'', max_length=255)),
                ('sequence', models.IntegerField(default=0)),
                ('name', models.CharField(default=b'', max_length=255)),
                ('x', models.DecimalField(max_digits=30, decimal_places=25)),
                ('y', models.DecimalField(max_digits=30, decimal_places=25)),
                ('width', models.DecimalField(max_digits=30, decimal_places=25)),
                ('height', models.DecimalField(max_digits=30, decimal_places=25)),
                ('image_width', models.DecimalField(null=True, max_digits=30, decimal_places=25, blank=True)),
                ('image_height', models.DecimalField(null=True, max_digits=30, decimal_places=25, blank=True)),
                ('image_file', models.ForeignKey(related_name='layout_image', blank=True, to='layout.ImageProperties', null=True)),
            ],
        ),
    ]
