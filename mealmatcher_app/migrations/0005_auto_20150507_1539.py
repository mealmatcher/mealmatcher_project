# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mealmatcher_app', '0004_auto_20150426_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='meal',
            name='user1',
            field=models.CharField(max_length=100, verbose_name=b'Person 1 username', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='meal',
            name='user2',
            field=models.CharField(max_length=100, verbose_name=b'Person 2 username', blank=True),
            preserve_default=True,
        ),
    ]
