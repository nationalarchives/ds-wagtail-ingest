from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page
from wagtail.search import index

from taggit.models import TagBase, ItemBase


class ResearchGuideTag(TagBase):
    free_tagging = False

    class Meta:
        verbose_name = "Research Guide Tag"


class TaggedResearchGuide(ItemBase):
    tag = models.ForeignKey(
        ResearchGuideTag,
        related_name="+",
        on_delete=models.CASCADE,
    )
    content_object = ParentalKey(
        "research.ResearchGuidePage",
        on_delete=models.CASCADE,
        related_name="tagged_research_guide_pages",
    )


class ResearchGuideIndexPage(Page):
    """Stub content for Research Guide Index

    - https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/
    """

    parent_page_types = ["home.HomePage"]
    subpage_types = ["research.ResearchGuidePage"]
    max_count = 1


class ResearchGuidePage(Page):
    """Stub content for a Research Guide

    - https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/recommendations-military-honours-awards-1935-1990/
    """

    source_url = models.URLField()
    research_guide_tags = ClusterTaggableManager(
        through=TaggedResearchGuide, blank=True
    )

    content_panels = [
        FieldPanel("source_url"),
        FieldPanel("research_guide_tags"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("source_url"),
        index.RelatedFields(
            "research_guide_tags",
            [
                index.SearchField("name"),
                index.FilterField("slug"),
            ],
        ),
    ]

    parent_page_types = ["research.ResearchGuideIndexPage"]
    subpage_types = []
