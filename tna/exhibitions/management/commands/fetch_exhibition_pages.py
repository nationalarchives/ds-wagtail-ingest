import django

import requests
import requests_cache

from pyquery import PyQuery as pq

from django.core.management.base import BaseCommand

from ....home.models import HomePage
from ...models import (
    ExhibitionIndexPage,
    ExhibitionPage,
)

DATEIME_FORMAT = "%A %d %B %Y"

requests_cache.install_cache("research-guides")


def fetch_page_data():
    base_url = f"https://www.nationalarchives.gov.uk/online-exhibitions/?sorted-by=a-z-by-title"
    page = requests.get(base_url).content
    document = pq(page)

    for a in document.find(".row .breather a"):
        anchor = pq(a)
        yield {
            "url": anchor.attr["href"].strip(),
            "title": anchor.find("h2").text(),
            "description": anchor.find("p").text(),
        }


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        home_page = HomePage.objects.get()

        try:
            exhibition_index_page = ExhibitionIndexPage.objects.get()
        except ExhibitionIndexPage.DoesNotExist:
            exhibition_index_page = ExhibitionIndexPage(title="Exhbitions")
            home_page.add_child(instance=exhibition_index_page)

        for page_data in fetch_page_data():

            try:
                exhibition_page = ExhibitionPage.objects.get(
                    source_url=page_data["url"]
                )
            except ExhibitionPage.DoesNotExist:
                exhibition_page = ExhibitionPage(source_url=page_data["url"])

            exhibition_page.title = page_data["title"]
            exhibition_page.description = page_data["description"]

            if not exhibition_page.id:
                exhibition_index_page.add_child(instance=exhibition_page)
            else:
                exhibition_page.save()
