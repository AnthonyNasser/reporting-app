# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-14 18:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0020_auto_20161208_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='message',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]