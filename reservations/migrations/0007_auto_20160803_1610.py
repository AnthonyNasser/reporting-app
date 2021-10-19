# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0006_auto_20160803_1330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='items',
            field=models.ManyToManyField(to='reservations.Item', related_name='in_reservations'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='user',
            field=models.ForeignKey(to='reservations.User', related_name='has_reservations'),
        ),
    ]
