from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from taggit.models import TagBase, ItemBase

from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Page


class SuitableForTag(TagBase):
    free_tagging = False

    class Meta:
        verbose_name = "Suitable for"


class TimePeriodTag(TagBase):
    free_tagging = False

    class Meta:
        verbose_name = "Suitable for"


class TopicTag(TagBase):
    free_tagging = False

    class Meta:
        verbose_name = "Topic"


class TaggedSuitableForLearningResourceTag(ItemBase):
    tag = models.ForeignKey(
        SuitableForTag,
        related_name="+",
        on_delete=models.CASCADE,
    )
    content_object = ParentalKey(
        "lessons.LearningResourcePage",
        on_delete=models.CASCADE,
        related_name="tagged_suitable_for_items",
    )


class TaggedTopicLearningResourceTag(ItemBase):
    tag = models.ForeignKey(
        TopicTag,
        related_name="+",
        on_delete=models.CASCADE,
    )
    content_object = ParentalKey(
        "lessons.LearningResourcePage",
        on_delete=models.CASCADE,
        related_name="tagged_topics",
    )


class TaggedTimePeriodLearningResourceTag(ItemBase):
    tag = models.ForeignKey(
        TimePeriodTag,
        related_name="+",
        on_delete=models.CASCADE,
    )
    content_object = ParentalKey(
        "lessons.LearningResourcePage",
        on_delete=models.CASCADE,
        related_name="tagged_time_period_items",
    )


class LearningResourceIndexPage(Page):
    parent_page_types = ["home.HomePage"]
    subpage_types = ["lessons.LearningResourcePage"]
    max_count = 1


class LearningResourcePage(Page):
    source_url = models.URLField()
    sub_title = models.CharField(max_length=255)
    body = RichTextField()
    suitable_for_tags = ClusterTaggableManager(
        through=TaggedSuitableForLearningResourceTag, blank=True
    )
    topic_tags = ClusterTaggableManager(
        through=TaggedTopicLearningResourceTag, blank=True
    )
    time_period_tags = ClusterTaggableManager(
        through=TaggedTimePeriodLearningResourceTag, blank=True
    )
    suggested_inquiry_question = models.CharField(max_length=512, blank=True)
    potential_activities = models.CharField(max_length=512, blank=True)

    content_panels = [
        FieldPanel("source_url"),
        FieldPanel("title"),
        FieldPanel("sub_title"),
        FieldPanel("body"),
        FieldPanel("suitable_for_tags", heading="Suitable for"),
        FieldPanel("topic_tags", heading="Topics"),
        FieldPanel("time_period_tags", heading="Time period"),
        FieldPanel("suggested_inquiry_question"),
        FieldPanel("potential_activities"),
    ]

    parent_page_types = ["lessons.LearningResourceIndexPage"]
    subpage_types = []

    def __str__(self):
        return self.title
