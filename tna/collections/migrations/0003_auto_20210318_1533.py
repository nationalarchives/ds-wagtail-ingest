# Generated by Django 3.1.6 on 2021-03-18 15:33

from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('collections', '0002_auto_20210318_1526'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='record',
            name='categories',
        ),
        migrations.AddField(
            model_name='category',
            name='records',
            field=modelcluster.fields.ParentalManyToManyField(related_name='categories', to='collections.Record'),
        ),
    ]
