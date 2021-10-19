# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0004_reservation_checkin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='crew',
        ),
        migrations.AddField(
            model_name='reservation',
            name='crew',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='project',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='title',
            field=models.CharField(default='S', max_length=1, choices=[('S', 'Staff')]),
        ),
        migrations.DeleteModel(
            name='Project',
        ),
    ]
