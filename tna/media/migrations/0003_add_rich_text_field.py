# Generated by Django 3.1.6 on 2022-03-18 17:43

from django.db import migrations
import tna.richtext.fields


class Migration(migrations.Migration):

    dependencies = [
        ("media", "0002_auto_20210216_1518"),
    ]

    operations = [
        migrations.AlterField(
            model_name="audiopage",
            name="body",
            field=tna.richtext.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name="videopage",
            name="body",
            field=tna.richtext.fields.RichTextField(),
        ),
    ]
