# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(verbose_name=b'Date of meal')),
                ('time', models.CharField(max_length=1, choices=[(b'B', b'Breakfast'), (b'L', b'Lunch'), (b'D', b'Dinner')])),
                ('location', models.CharField(max_length=2, choices=[(b'WH', b'Whitman'), (b'RM', b'Rocky/Mathey'), (b'BW', b'Butler/Wilson'), (b'F', b'Forbes')])),
                ('attire1', models.CharField(max_length=100, verbose_name=b'Person 1 Attire', blank=True)),
                ('attire2', models.CharField(max_length=100, verbose_name=b'Person 2 Attire', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='meal',
            name='users',
            field=models.ManyToManyField(to='mealmatcher_app.UserProfile'),
            preserve_default=True,
        ),
    ]
