from django.core.management.base import BaseCommand

import requests
import requests_cache

from pyquery import PyQuery as pq

from ...models import (
    Category,
    Record,
    CategoryRecord,
)

requests_cache.install_cache("/tmp/records")


def fetch_record_results(query, items_per_page=60):
    for i in range(1, 29):
        url = f"https://discovery.nationalarchives.gov.uk/results/r/{i}?_q={query}&_ps={items_per_page}"
        print(url)
        page = requests.get(url).content
        document = pq(page)

        for li in document.find("ul#search-results li"):
            meta = [pq(td).text() for td in pq(li).find("td")]
            yield {
                "href": pq(li).find("a").attr["href"],
                "name": pq(li).find("a h3").text(),
                "description": pq(li).find("a p").text(),
                "held_by": meta[0],
                "date": meta[1],
                "reference": meta[2],
            }


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        query = "Medieval deeds"

        category, _ = Category.objects.update_or_create(name=query)

        for record in fetch_record_results(query):
            record_object, created = Record.objects.update_or_create(
                reference=record["reference"],
                defaults={k: v for k, v in record.items() if k != "href"},
            )
            record_object.categories.set([CategoryRecord(category=category)])
            record_object.save()
