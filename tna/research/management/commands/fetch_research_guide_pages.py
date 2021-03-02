import requests
import requests_cache

from pyquery import PyQuery as pq

from django.core.management.base import BaseCommand

from ....home.models import HomePage
from ...models import (
    ResearchGuidePage,
    ResearchGuideIndexPage,
    ResearchGuideTag,
)

DATEIME_FORMAT = "%A %d %B %Y"

requests_cache.install_cache("/tmp/research-guides")


def fetch_page_data():
    base_url = (
        f"https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/"
    )
    page = requests.get(base_url).content
    document = pq(page)

    for a in document.find(".resource-results ul > li > a"):
        yield {
            'title':a.text, 
            'url':a.attrib["href"], 
            'tags': [a.text.strip().title() for a in pq(a).siblings('span.tag a')]
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
                page = ResearchGuidePage.objects.get(source_url=page_data['url'])
            except ResearchGuidePage.DoesNotExist:
                page = ResearchGuidePage(source_url=page_data['url'])

            page.title = page_data['title']

            for name in page_data['tags']:
                if not page.research_guide_tags.filter(name=name).exists():
                    tag, _ = ResearchGuideTag.objects.get_or_create(name=name)
                    page.research_guide_tags.add(tag)

            if not page.id:
                research_guide_index_page.add_child(instance=page)
            else:
                page.save()

