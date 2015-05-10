# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mealmatcher_app', '0005_auto_20150507_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='disabled_status',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
    ]
