# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0002_auto_20150908_1308'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='item',
            options={'ordering': ['label', 'name']},
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='volunteers',
        ),
        migrations.AddField(
            model_name='reservation',
            name='crew',
            field=models.ManyToManyField(related_name='crew', to='reservations.User'),
        ),
        migrations.AlterField(
            model_name='item',
            name='label',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='sid',
            field=models.CharField(max_length=12, verbose_name='Student ID'),
        ),
        migrations.AlterField(
            model_name='user',
            name='title',
            field=models.CharField(choices=[('S', 'Staff'), ('C', 'Crew')], max_length=1, default='C'),
        ),
    ]
