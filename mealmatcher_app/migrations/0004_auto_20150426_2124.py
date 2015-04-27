# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mealmatcher_app', '0003_auto_20150419_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal',
            name='location',
            field=models.CharField(max_length=2, choices=[(b'WH', b'Whitman'), (b'RM', b'Rocky'), (b'BW', b'Butler'), (b'MR', b'Mathey'), (b'WB', b'Wilson'), (b'F', b'Forbes')]),
            preserve_default=True,
        ),
    ]
