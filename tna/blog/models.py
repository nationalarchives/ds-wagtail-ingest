from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey

from taggit.models import ItemBase

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page

from ..collections.models import ThemeTag, CategoryTag


class TaggedThemeBlogPageItem(ItemBase):
    tag = models.ForeignKey(
        ThemeTag, related_name="tagged_blog_page_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "blog.BlogPage",
        on_delete=models.CASCADE,
        related_name="tagged_blog_page_items",
    )


class TaggedCategoryBlogPageItem(ItemBase):
    tag = models.ForeignKey(
        CategoryTag, related_name="tagged_blog_page_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "blog.BlogPage",
        on_delete=models.CASCADE,
        related_name="tagged_category_items",
    )


class BlogIndexPage(Page):
    ...


class BlogPage(Page):
    source_url = models.URLField()
    body = models.TextField()
    date_published = models.DateTimeField()
    content_tags = ClusterTaggableManager(
        through=TaggedCategoryBlogPageItem, blank=True
    )
    theme_tags = ClusterTaggableManager(through=TaggedThemeBlogPageItem, blank=True)

    content_panels = [
        FieldPanel("source_url"),
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("date_published"),
        FieldPanel("content_tags", heading="Content tags"),
        FieldPanel("theme_tags", heading="Theme tags"),
    ]

    def __str__(self):
        return self.title