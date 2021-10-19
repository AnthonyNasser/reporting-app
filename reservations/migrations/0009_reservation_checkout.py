# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0008_auto_20160804_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='checkout',
            field=models.BooleanField(default=False),
        ),
    ]
