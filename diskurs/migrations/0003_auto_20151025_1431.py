# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diskurs', '0002_auto_20151010_0959'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='post_nr_in_thread_by_user',
        ),
        migrations.AlterField(
            model_name='post',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
