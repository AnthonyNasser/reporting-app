# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0005_auto_20160803_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='project',
            field=models.CharField(max_length=100),
        ),
    ]
