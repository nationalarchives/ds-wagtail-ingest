from itertools import chain

from django.apps import apps
from django.db import models
from django.http import HttpResponseRedirect

from wagtail.core.models import Page
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel

from modelcluster.fields import ParentalManyToManyField, ParentalKey
from modelcluster.models import ClusterableModel


@register_snippet
class Record(ClusterableModel):
    name = models.CharField(max_length=240)
    description = models.TextField()
    held_by = models.TextField()
    date = models.CharField(max_length=120)
    reference = models.CharField(max_length=120)

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("date"),
        FieldPanel("reference"),
        InlinePanel("categories", label="Categories"),
    ]

    def __str__(self):
        return self.name


@register_snippet
class Category(models.Model):
    name = models.CharField(max_length=120)

    class Meta:
        verbose_name_plural = "Categories"

    panels = [
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name


class CategoryRecord(models.Model):
    record = ParentalKey("Record", on_delete=models.CASCADE, related_name="categories")
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, related_name="records"
    )

    panels = [
        SnippetChooserPanel("category"),
    ]


class PageCategory(models.Model):
    Page = ParentalKey(
        "collections.CategoryPage", on_delete=models.CASCADE, related_name="categories"
    )
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, related_name="pages"
    )

    panels = [
        SnippetChooserPanel("category"),
    ]


class ExplorerPage(Page):
    introduction = models.CharField(max_length=200)

    content_panels = Page.content_panels + [FieldPanel("introduction")]

    max_count = 1
    parent_page_types = ["home.HomePage"]
    subpage_types = ["collections.CategoryPage"]


class CategoryPage(Page):

    """
    Time periods > Medieval > Magna Carta
    """

    introduction = models.TextField()

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        InlinePanel("categories", label="Categories"),
    ]

    @property
    def has_results_page(self):
        return self.get_children().type(FilterPage).exists()

    def serve(self, request):
        if self.has_results_page:
            results_page = self.get_children().type(FilterPage).first()
            return HttpResponseRedirect(results_page.get_url())
        return super().serve(request)

    def get_template(self, request, *args, **kwargs):
        if self.get_children().first().specific.has_results_page:
            return "collections/category_page_before_results_page.html"
        return super().get_template(request)

    parent_page_types = ["collections.ExplorerPage", "collections.CategoryPage"]
    subpage_types = ["collections.CategoryPage", "collections.FilterPage"]


class FilterPage(Page):
    """Results page?"""

    def get_context(self, request):
        context = super().get_context(request)
        ancestor_category_pages = (
            self.get_ancestors().specific(defer=True).type(CategoryPage)
        )
        categories = chain.from_iterable(
            [
                p.categories.values_list("category", flat=True)
                for p in ancestor_category_pages
            ]
        )
        context["results"] = Record.objects.filter(
            categories__category__in=[id for id in categories]
        )

        return context

    max_count_per_parent = 1
    parent_page_types = ["collections.CategoryPage"]
    subpage_types = []
