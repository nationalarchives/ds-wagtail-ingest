import requests
import requests_cache

from pyquery import PyQuery as pq

from django.core.management.base import BaseCommand

from ....home.models import HomePage
from ...models import (
    ResearchGuidePage,
    ResearchGuideIndexPage,
    ResearchGuideTag,
    TaggedResearchGuide, 
)

DATEIME_FORMAT = "%A %d %B %Y"

requests_cache.install_cache("research-guides")


def fetch_page_data():
    base_url = (
        f"https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/"
    )
    page = requests.get(base_url).content
    document = pq(page)

    for a in document.find(".resource-results ul > li > a"):
        tags = {a.attrib['href']: a.text for a in pq(a).siblings('span.tag a')}
        yield {
            'title':a.text, 
            'url':a.attrib["href"], 
            'tags': tags
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

            try:
                research_guide = ResearchGuidePage.objects.get(source_url=page_data['url'])
            except ResearchGuidePage.DoesNotExist:
                research_guide = ResearchGuidePage(source_url=page_data['url'])

            research_guide.title = page_data['title']

            if not research_guide.id:
                research_guide_index_page.add_child(instance=research_guide)

            research_guide_tags = [
                ResearchGuideTag.objects.get_or_create(name=tag_name.title())[0]
                for tag_href, tag_name in page_data['tags'].items()
            ]

            for tag in research_guide_tags:
                TaggedResearchGuide.objects.create(tag=tag, content_object=research_guide)
