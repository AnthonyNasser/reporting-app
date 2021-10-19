# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-22 20:19
from __future__ import unicode_literals

import api_wellness.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=75)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'activities',
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('code', models.CharField(choices=[('BLM', 'Log-in Master'), ('BSS', 'Swift Swimmer'), ('BGR', 'Gym Rat'), ('BRC', 'Rock Wall Challenger'), ('BIA', 'Inclusive Activist'), ('BOA', 'Outdoor Adventurer'), ('BLC', 'League Champ'), ('BGM', 'Game Master'), ('BWW', 'Wellness Warrior'), ('BBC', 'Beach Pride Champion')], max_length=3)),
                ('description', models.TextField()),
                ('message', models.TextField()),
                ('icon', models.ImageField(upload_to=api_wellness.models.badge_directory_path, verbose_name='Badge Icon')),
                ('points', models.PositiveSmallIntegerField()),
            ],
            options={
                'ordering': [],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=75)),
                ('description', models.TextField(blank=True)),
                ('active', models.BooleanField(default=True)),
                ('points', models.PositiveSmallIntegerField(default=1)),
            ],
            options={
                'verbose_name_plural': 'categories',
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=75)),
                ('description', models.TextField(blank=True)),
                ('active', models.BooleanField(default=True)),
                ('poster', models.ImageField(upload_to=api_wellness.models.event_directory_path, verbose_name='Event Poster')),
                ('points', models.PositiveSmallIntegerField(default=8)),
                ('promote', models.BooleanField(default=False)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('location', models.CharField(max_length=150)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-start', 'name'],
            },
        ),
        migrations.CreateModel(
            name='EventLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_wellness.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('datetime', models.DateTimeField()),
            ],
            options={
                'verbose_name_plural': 'feedback',
            },
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('M1', 'Milestone 1'), ('M2', 'Milestone 2'), ('M3', 'Milestone 3'), ('M4', 'Milestone 4'), ('M5', 'Milestone 5')], max_length=2)),
                ('points', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('id', models.CharField(max_length=10, unique=True, verbose_name='Student/Employee ID')),
                ('dob', models.DateField(blank=True, null=True, verbose_name='Date of Birth')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=api_wellness.models.avatar_directory_path, verbose_name='Profile Picture')),
                ('gender', models.CharField(blank=True, choices=[('', 'Please select your gender'), ('MALE', 'Man'), ('FEMA', 'Woman'), ('QUEE', 'Queer'), ('QTMA', 'Queer Transmasculine'), ('QTFE', 'Queer Transfeminine'), ('NBIN', 'Non-binary'), ('ANON', 'Prefer not to disclose')], max_length=4)),
                ('dept', models.CharField(choices=[('', 'Please select your department'), ('CDC', 'Isabel Patterson Child Development Center'), ('BO', 'Business Office'), ('HR', 'Human Resources'), ('IT', 'IT'), ('GOV', 'Student Government'), ('BPE', 'Beach Pride Events'), ('COM', 'ASI Communications'), ('SM', 'Student Media'), ('FM', 'Facilities & Maintenance'), ('RC', 'Recycling Center'), ('UBM', 'USU - Building Managers'), ('CE', 'Conference & Events'), ('MBP', 'Maxson & Beach Pantry'), ('GCI', 'Games, Candy, Info & Ticket Center'), ('FIT', 'SRWC - Fitness'), ('INT', 'SRWC - Intramurals'), ('AQU', 'SRWC - Aquatics'), ('MB', 'SRWC - Membership'), ('RBB', 'SRWC - ROA/Beach Balance'), ('MA', 'SRWC - Membership & Admin'), ('SBM', 'SRWC - Building Managers')], max_length=3, verbose_name='Department')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=75)),
                ('description', models.TextField(blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('badge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_wellness.Badge')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_wellness.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='UserMilestone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('milestone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_wellness.Milestone')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_wellness.Profile')),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='badges',
            field=models.ManyToManyField(related_name='users', through='api_wellness.UserBadge', to='api_wellness.Badge'),
        ),
        migrations.AddField(
            model_name='profile',
            name='categories',
            field=models.ManyToManyField(related_name='users', through='api_wellness.ActivityLog', to='api_wellness.Category'),
        ),
        migrations.AddField(
            model_name='profile',
            name='events',
            field=models.ManyToManyField(related_name='users', through='api_wellness.EventLog', to='api_wellness.Event'),
        ),
        migrations.AddField(
            model_name='profile',
            name='milestones',
            field=models.ManyToManyField(related_name='users', through='api_wellness.UserMilestone', to='api_wellness.Milestone'),
        ),
        migrations.AddField(
            model_name='feedback',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='get_user_feedback', to='api_wellness.Profile'),
        ),
        migrations.AddField(
            model_name='eventlog',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_wellness.Profile'),
        ),
        migrations.AddField(
            model_name='event',
            name='section',
            field=models.ForeignKey(default=api_wellness.models.Section.event_default, on_delete=django.db.models.deletion.PROTECT, related_name='events', to='api_wellness.Section'),
        ),
        migrations.AddField(
            model_name='category',
            name='section',
            field=models.ForeignKey(default=api_wellness.models.Section.section_default, on_delete=django.db.models.deletion.PROTECT, related_name='categories', to='api_wellness.Section'),
        ),
        migrations.AddField(
            model_name='activitylog',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_wellness.Category'),
        ),
        migrations.AddField(
            model_name='activitylog',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_wellness.Profile'),
        ),
        migrations.AddField(
            model_name='activity',
            name='category',
            field=models.ForeignKey(default=api_wellness.models.Category.category_default, on_delete=django.db.models.deletion.PROTECT, related_name='activities', to='api_wellness.Category'),
        ),
        migrations.AlterUniqueTogether(
            name='usermilestone',
            unique_together=set([('profile', 'milestone')]),
        ),
        migrations.AlterUniqueTogether(
            name='userbadge',
            unique_together=set([('profile', 'badge')]),
        ),
        migrations.AlterUniqueTogether(
            name='eventlog',
            unique_together=set([('profile', 'event')]),
        ),
        migrations.AlterUniqueTogether(
            name='activitylog',
            unique_together=set([('profile', 'datetime')]),
        ),
    ]