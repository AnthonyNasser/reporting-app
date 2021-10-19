# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0009_reservation_checkout'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reservation',
            options={'ordering': ['start_date', 'start_time', 'project']},
        ),
        migrations.RenameField(
            model_name='reservation',
            old_name='end',
            new_name='end_time',
        ),
        migrations.RenameField(
            model_name='reservation',
            old_name='date',
            new_name='start_date',
        ),
        migrations.RenameField(
            model_name='reservation',
            old_name='start',
            new_name='start_time',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='approved',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='checkin',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='checkout',
        ),
        migrations.AddField(
            model_name='reservation',
            name='end_date',
            field=models.DateField(default=django.utils.timezone.now, max_length=10),
        ),
        migrations.AddField(
            model_name='reservation',
            name='state',
            field=models.CharField(default='RSVD', choices=[('RSVD', 'Reserved'), ('APRV', 'Approved'), ('COUT', 'Checkout'), ('CIN', 'Checkin')], max_length=4),
        ),
    ]
