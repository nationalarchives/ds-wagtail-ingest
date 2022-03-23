from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.documents import get_document_model_string
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.search import index

from taggit.models import ItemBase, TagBase

from ..collections.models import CategoryTag, ThemeTag
from ..richtext.fields import RichTextField


class TaggedThemeAudioItem(ItemBase):
    tag = models.ForeignKey(
        ThemeTag, related_name="tagged_audio_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "media.AudioPage",
        on_delete=models.CASCADE,
        related_name="tagged_theme_items",
    )


class TaggedCategoryAudioItem(ItemBase):
    tag = models.ForeignKey(
        CategoryTag, related_name="tagged_audio_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "media.AudioPage",
        on_delete=models.CASCADE,
        related_name="tagged_content_items",
    )


class AudioIndexPage(Page):
    max_count = 1
    parent_page_types = ["home.HomePage"]
    subpage_types = ["media.AudioPage"]


class AudioPage(Page):
    source_url = models.URLField()
    body = RichTextField()
    date_published = models.DateTimeField()
    file = models.ForeignKey(
        get_document_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    content_tags = ClusterTaggableManager(through=TaggedCategoryAudioItem, blank=True)
    theme_tags = ClusterTaggableManager(through=TaggedThemeAudioItem, blank=True)

    content_panels = [
        FieldPanel("source_url"),
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("date_published"),
        FieldPanel("content_tags", heading="Content tags"),
        FieldPanel("theme_tags", heading="Theme tags"),
        DocumentChooserPanel("file"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("source_url"),
        index.SearchField("body"),
        index.RelatedFields(
            "content_tags",
            [
                index.SearchField("name"),
                index.FilterField("slug"),
            ],
        ),
        index.RelatedFields(
            "theme_tags",
            [
                index.SearchField("name"),
                index.FilterField("slug"),
            ],
        ),
    ]

    parent_page_types = ["media.AudioIndexPage"]
    subpage_types = []

    def __str__(self):
        return self.title


class TaggedThemeVideoItem(ItemBase):
    tag = models.ForeignKey(
        ThemeTag, related_name="tagged_video_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "media.VideoPage",
        on_delete=models.CASCADE,
        related_name="tagged_video_items",
    )


class TaggedCategoryVideoItem(ItemBase):
    tag = models.ForeignKey(
        CategoryTag, related_name="tagged_video_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "media.VideoPage",
        on_delete=models.CASCADE,
        related_name="tagged_category_items",
    )


class VideoIndexPage(Page):
    max_count = 1
    parent_page_types = ["home.HomePage"]
    subpage_types = ["media.VideoPage"]


class VideoPage(Page):
    source_url = models.URLField()
    body = RichTextField()
    date_published = models.DateTimeField()
    file = models.ForeignKey(
        get_document_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    content_tags = ClusterTaggableManager(through=TaggedCategoryVideoItem, blank=True)
    theme_tags = ClusterTaggableManager(through=TaggedThemeVideoItem, blank=True)

    content_panels = [
        FieldPanel("source_url"),
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("date_published"),
        FieldPanel("content_tags", heading="Content tags"),
        FieldPanel("theme_tags", heading="Theme tags"),
        DocumentChooserPanel("file"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("source_url"),
        index.SearchField("body"),
        index.RelatedFields(
            "content_tags",
            [
                index.SearchField("name"),
                index.FilterField("slug"),
            ],
        ),
        index.RelatedFields(
            "theme_tags",
            [
                index.SearchField("name"),
                index.FilterField("slug"),
            ],
        ),
    ]

    parent_page_types = ["media.VideoIndexPage"]
    subpage_types = []

    def __str__(self):
        return self.title
