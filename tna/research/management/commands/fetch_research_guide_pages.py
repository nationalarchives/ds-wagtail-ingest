import csv

import requests
import requests_cache

from pyquery import PyQuery as pq

from django.core.management.base import BaseCommand

from ....home.models import HomePage
from ...models import (
    ResearchGuidePage,
    ResearchGuideIndexPage,
    ResearchGuideTag,
    CategoryTag,
)

DATEIME_FORMAT = "%A %d %B %Y"

requests_cache.install_cache("/tmp/research-guides")


def find_shared_tag(research_guide_tag):
    with open("terms.csv") as file:
        for row in csv.reader(file, delimiter=","):
            source = row[0]
            topic = row[1]
            category = row[5]
            sub_category = row[6]

            if not topic:
                continue

            if category.lower() == research_guide_tag.lower():
                return source, topic

            if sub_category.lower() == research_guide_tag.lower():
                return source, topic

            if research_guide_tag.lower() in category.lower():
                return source, topic

            if research_guide_tag.lower() in sub_category.lower():
                return source, topic

        raise Exception(f'Unmatched tag: {research_guide_tag}')


def get_tag_class(source):
    return CategoryTag


# source, topic = find_shared_tag('caribbean')
# cls = get_tag_class(source)
# category_tag = cls.objects.get_or_create(name=topic)
# import ipdb; ipdb.set_trace()


def fetch_page_data():
    base_url = (
        f"https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/"
    )
    page = requests.get(base_url).content
    document = pq(page)

    for a in document.find(".resource-results ul > li > a"):

        url = a.attrib["href"]
        research_guide_document = pq(requests.get(url).content)
        body = research_guide_document.find("#research-guide-content").html() or ""

        yield {
            "title": a.text,
            "url": url,
            "body": body,
            "tags": [a.text.strip().title() for a in pq(a).siblings("span.tag a")],
        }


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        home_page = HomePage.objects.get()

        try:
            research_guide_index_page = ResearchGuideIndexPage.objects.get()
        except ResearchGuideIndexPage.DoesNotExist:
            research_guide_index_page = ResearchGuideIndexPage(title="Research Guides")
            home_page.add_child(instance=research_guide_index_page)

        for page_data in fetch_page_data():

            print(f"Fetching {page_data['url']}")

            try:
                page = ResearchGuidePage.objects.get(source_url=page_data["url"])
            except ResearchGuidePage.DoesNotExist:
                page = ResearchGuidePage(source_url=page_data["url"])

            page.title = page_data["title"]
            page.body = page_data["body"]

            for name in page_data["tags"]:
                if not page.research_guide_tags.filter(name=name).exists():
                    tag, _ = ResearchGuideTag.objects.get_or_create(name=name)
                    page.research_guide_tags.add(tag)

            for tag in page.research_guide_tags.all():
                try:
                    source, topic = find_shared_tag(tag.name)
                except Exception as e:
                    print(e)
                    continue
                cls = get_tag_class(source)
                category_tag, created = cls.objects.get_or_create(name=topic)
                page.category_tags.add(category_tag)

            if not page.pk:
                research_guide_index_page.add_child(instance=page)
            else:
                page.save()
