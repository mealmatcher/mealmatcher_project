# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mealmatcher_app', '0002_auto_20150403_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal',
            name='meal_time',
            field=models.CharField(max_length=1, choices=[(b'B', b'Breakfast'), (b'L', b'Lunch'), (b'D', b'Dinner'), (b'R', b'Brunch')]),
            preserve_default=True,
        ),
    ]
