# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('model', models.CharField(blank=True, max_length=30)),
                ('label', models.CharField(blank=True, max_length=30)),
                ('serial', models.CharField(blank=True, max_length=30)),
                ('condition', models.CharField(choices=[('G', 'Good'), ('F', 'Fair'), ('D', 'Damage')], max_length=1, default='G')),
                ('misc', models.TextField(blank=True)),
                ('available', models.CharField(choices=[('1', 'Yes'), ('0', 'No')], max_length=1, default='1')),
                ('category', models.ForeignKey(related_name='items', to='reservations.Category')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=8, default='#00CC00')),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('date', models.DateField(max_length=10, default=django.utils.timezone.now)),
                ('start', models.TimeField(verbose_name='start time', max_length=8)),
                ('end', models.TimeField(verbose_name='end time', max_length=8)),
                ('comment', models.TextField(blank=True)),
                ('items', models.ManyToManyField(related_name='items', to='reservations.Item')),
                ('project', models.ForeignKey(related_name='projects', to='reservations.Project')),
            ],
            options={
                'ordering': ['date', 'start', 'project'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=10)),
                ('sid', models.CharField(verbose_name='student ID', max_length=12)),
                ('title', models.CharField(choices=[('E', 'Editor'), ('P', 'Producer'), ('V', 'Volunteer')], max_length=1, default='V')),
            ],
        ),
        migrations.AddField(
            model_name='reservation',
            name='user',
            field=models.ForeignKey(related_name='users', to='reservations.User'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='volunteers',
            field=models.ManyToManyField(related_name='volunteers', to='reservations.User'),
        ),
    ]
