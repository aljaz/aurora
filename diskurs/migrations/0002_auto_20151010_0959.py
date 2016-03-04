# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diskurs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='parent_post',
            field=models.ForeignKey(blank=True, to='diskurs.Post', null=True),
        ),
    ]
