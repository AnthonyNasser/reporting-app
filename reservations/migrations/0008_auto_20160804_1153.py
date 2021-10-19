# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0007_auto_20160803_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='items',
            field=models.ManyToManyField(related_name='reservations', to='reservations.Item'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='user',
            field=models.ForeignKey(related_name='reservations', to='reservations.User'),
        ),
    ]
