from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page
from wagtail.search import index

from taggit.models import TagBase

from ..richtext.fields import RichTextField


class ThemeTag(TagBase):
    free_tagging = False

    class Meta:
        verbose_name = "theme tag"


class CategoryTag(TagBase):
    free_tagging = False

    class Meta:
        verbose_name = "Category tag"


class ResultsIndexPage(Page):
    max_count = 1
    parent_page_types = ["home.HomePage"]
    subpage_types = ["collections.ResultsPage"]


class ResultsPage(Page):
    source_url = models.URLField()
    body = RichTextField()

    content_panels = [
        FieldPanel("source_url"),
        FieldPanel("title"),
        FieldPanel("body"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("source_url"),
        index.SearchField("body"),
    ]

    parent_page_types = ["collections.ResultsIndexPage"]
    subpage_types = []

    def __str__(self):
        return self.title
