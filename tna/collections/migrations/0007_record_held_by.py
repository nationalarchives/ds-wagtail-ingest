# Generated by Django 3.1.6 on 2021-03-23 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collections', '0006_pagecategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='held_by',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
