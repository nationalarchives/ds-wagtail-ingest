from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page


class ExhibitionIndexPage(Page):
    """Stub content for Exhibitions

    - https://www.nationalarchives.gov.uk/online-exhibitions/?sorted-by=a-z-by-title
    """

    parent_page_types = ["home.HomePage"]
    subpage_types = ["exhibitions.ExhibitionPage"]
    max_count = 1


class ExhibitionPage(Page):
    """Stub content for an exhibition

    - https://www.nationalarchives.gov.uk/railways/
    """

    source_url = models.URLField()
    description = models.TextField()

    content_panels = [
        FieldPanel("source_url"),
        FieldPanel("description"),
    ]

    parent_page_types = ["exhibitions.ExhibitionPage"]
