# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0013_auto_20160812_1240'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='available',
        ),
    ]
