# Generated by Django 3.1.6 on 2021-02-03 12:06

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('collections', '0006_audioindexpage_videoindexpage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contenthubpage',
            name='body',
            field=wagtail.core.fields.StreamField([('paragraph_with_podcast', wagtail.core.blocks.StructBlock([('paragraph', wagtail.core.blocks.RichTextBlock()), ('page', wagtail.core.blocks.PageChooserBlock())]))]),
        ),
    ]