# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0003_auto_20160406_1105'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='checkin',
            field=models.BooleanField(default=False),
        ),
    ]
