# Generated by Django 3.1.6 on 2021-02-03 15:22

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='taggedsuitableforlearningresourcetag',
            name='content_object',
            field=modelcluster.fields.ParentalKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='tagged_suitable_for_items', to='lessons.learningresourcepage'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='taggedsuitableforlearningresourcetag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='lessons.suitablefortag'),
        ),
        migrations.CreateModel(
            name='TaggedTopicLearningResourceTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagged_topics', to='lessons.learningresourcepage')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='lessons.topictag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaggedTimePeriodLearningResourceTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagged_time_period_items', to='lessons.learningresourcepage')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='lessons.timeperiodtag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='learningresourcepage',
            name='time_period_tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='lessons.TaggedTimePeriodLearningResourceTag', to='lessons.TimePeriodTag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='learningresourcepage',
            name='topic_tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='lessons.TaggedTopicLearningResourceTag', to='lessons.TopicTag', verbose_name='Tags'),
        ),
    ]
