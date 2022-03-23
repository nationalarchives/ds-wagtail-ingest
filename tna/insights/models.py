from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page
from wagtail.search import index

from ..richtext.fields import RichTextField


class InsightsIndexPage(Page):
    max_count = 1
    parent_page_types = ["home.HomePage"]
    subpage_types = ["insights.InsightsPage"]


class InsightsPage(Page):
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

    parent_page_types = ["insights.InsightsIndexPage"]
    subpage_types = []

    def __str__(self):
        return self.title
