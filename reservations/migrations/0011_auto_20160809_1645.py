# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0010_auto_20160809_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='state',
            field=models.IntegerField(default=1, choices=[(1, 'Reserved'), (2, 'Approved'), (3, 'Checkout'), (4, 'Checkin')]),
        ),
    ]
