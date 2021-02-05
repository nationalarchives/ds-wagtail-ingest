from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from taggit.models import TagBase, ItemBase

from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.documents import get_document_model_string

from .blocks import ContentHubBodyBlock


class ThemeTag(TagBase):
    free_tagging = False

    class Meta:
        verbose_name = "theme tag"


class CategoryTag(TagBase):
    free_tagging = False

    class Meta:
        verbose_name = "theme tag"


class TaggedThemeContentHubPageItem(ItemBase):
    tag = models.ForeignKey(
        ThemeTag, related_name="tagged_content_hub_page_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "collections.ContentHubPage",
        on_delete=models.CASCADE,
        related_name="tagged_content_hub_page_items",
    )


class TaggedCategoryContentHubPageItem(ItemBase):
    tag = models.ForeignKey(
        CategoryTag,
        related_name="tagged_content_hub_page_items",
        on_delete=models.CASCADE,
    )
    content_object = ParentalKey(
        "collections.ContentHubPage",
        on_delete=models.CASCADE,
        related_name="tagged_category_items",
    )


class ContentHubPage(Page):
    sub_title = models.CharField(max_length=255)
    body = StreamField(ContentHubBodyBlock())
    content_tags = ClusterTaggableManager(
        through=TaggedCategoryContentHubPageItem, blank=True
    )
    theme_tags = ClusterTaggableManager(
        through=TaggedThemeContentHubPageItem, blank=True
    )

    content_panels = [
        FieldPanel("title"),
        FieldPanel("sub_title"),
        StreamFieldPanel("body"),
        FieldPanel("content_tags", heading="Content tags"),
        FieldPanel("theme_tags", heading="Theme tags"),
    ]
