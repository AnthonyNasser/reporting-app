# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import reservations.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0014_remove_item_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.ForeignKey(default=reservations.models.Category.category_default, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='items', to='reservations.Category'),
        ),
        migrations.AlterField(
            model_name='user',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='users', to='reservations.Department'),
        ),
    ]
