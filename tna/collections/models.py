from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from taggit.models import TagBase, ItemBase
from taggit.managers import TaggableManager

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.documents import get_document_model_string
from wagtail.snippets.models import register_snippet


class ThemeTag(TagBase):
    free_tagging = False

    class Meta:
        verbose_name = "theme tag"


class CategoryTag(TagBase):
    free_tagging = False

    class Meta:
        verbose_name = "theme tag"


class TaggedThemeAudioItem(ItemBase):
    tag = models.ForeignKey(
        ThemeTag, related_name="tagged_audio_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "collections.Audio",
        on_delete=models.CASCADE,
        related_name="tagged_theme_items",
    )


class TaggedCategoryAudioItem(ItemBase):
    tag = models.ForeignKey(
        CategoryTag, related_name="tagged_audio_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "collections.Audio",
        on_delete=models.CASCADE,
        related_name="tagged_content_items",
    )


@register_snippet
class Audio(ClusterableModel):
    source_url = models.URLField()
    title = models.CharField(max_length=255)
    body = models.TextField()
    date_published = models.DateTimeField()
    file = models.ForeignKey(
        get_document_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    content_tags = TaggableManager(through=TaggedCategoryAudioItem, blank=True)
    theme_tags = TaggableManager(through=TaggedThemeAudioItem, blank=True)

    panels = [
        FieldPanel("source_url"),
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("date_published"),
        FieldPanel("content_tags", heading="Content tags"),
        FieldPanel("theme_tags", heading="Theme tags"),
        DocumentChooserPanel("file"),
    ]

    def __str__(self):
        return self.title


class TaggedThemeVideoItem(ItemBase):
    tag = models.ForeignKey(
        ThemeTag, related_name="tagged_video_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "collections.Video",
        on_delete=models.CASCADE,
        related_name="tagged_video_items",
    )


class TaggedCategoryVideoItem(ItemBase):
    tag = models.ForeignKey(
        CategoryTag, related_name="tagged_video_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "collections.Video",
        on_delete=models.CASCADE,
        related_name="tagged_category_items",
    )


@register_snippet
class Video(ClusterableModel):
    source_url = models.URLField()
    title = models.CharField(max_length=255)
    body = models.TextField()
    date_published = models.DateTimeField()
    file = models.ForeignKey(
        get_document_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    content_tags = TaggableManager(through=TaggedCategoryVideoItem, blank=True)
    theme_tags = TaggableManager(through=TaggedThemeVideoItem, blank=True)

    panels = [
        FieldPanel("source_url"),
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("date_published"),
        FieldPanel("content_tags", heading="Content tags"),
        FieldPanel("theme_tags", heading="Theme tags"),
        DocumentChooserPanel("file"),
    ]

    def __str__(self):
        return self.title


class TaggedThemeBlogPageItem(ItemBase):
    tag = models.ForeignKey(
        ThemeTag, related_name="tagged_blog_page_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "collections.BlogPage",
        on_delete=models.CASCADE,
        related_name="tagged_blog_page_items",
    )


class TaggedCategoryBlogPageItem(ItemBase):
    tag = models.ForeignKey(
        CategoryTag, related_name="tagged_blog_page_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "collections.BlogPage",
        on_delete=models.CASCADE,
        related_name="tagged_category_items",
    )


class BlogIndexPage(Page):
    ...


class BlogPage(Page):
    source_url = models.URLField()
    body = models.TextField()
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

    panels = [
        FieldPanel("source_url"),
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("date_published"),
        FieldPanel("content_tags", heading="Content tags"),
        FieldPanel("theme_tags", heading="Theme tags"),
        DocumentChooserPanel("file"),
    ]

    def __str__(self):
        return self.title
