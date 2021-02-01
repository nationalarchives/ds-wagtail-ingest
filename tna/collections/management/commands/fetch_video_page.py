from django.utils import timezone
from datetime import datetime

import requests
import requests_cache

from pyquery import PyQuery as pq

from django.core.management.base import BaseCommand

from ...models import (
    Video,
    CategoryTag,
    ThemeTag,
    TaggedThemeVideoItem,
    TaggedCategoryVideoItem,
)

DATEIME_FORMAT = "%A %d %B %Y"

requests_cache.install_cache("video")


def fetch_audo_page_urls():
    for i in range(1, 29):
        base_url = (
            f"https://media.nationalarchives.gov.uk/index.php/category/video/page/{i}/"
        )
        page = requests.get(base_url).content
        document = pq(page)

        for a in document.find("a.content-card"):
            yield a.attrib["href"]


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        for url in fetch_audo_page_urls():
            page = requests.get(url).content
            document = pq(page)

            published_date_string = (
                document.find(".entry-meta").text().split("|")[0].strip()
            )
            published_date = datetime.strptime(published_date_string, DATEIME_FORMAT)
            published_date = timezone.make_aware(published_date)

            theme_tag_names = [a.text for a in document.find(".tags a")]
            theme_tags = [
                ThemeTag.objects.get_or_create(name=tag_name)[0]
                for tag_name in theme_tag_names
            ]

            category_tag_names = [
                t.strip()
                for t in document.find(".entry-meta").text().split("|")[2].split(",")
            ]
            category_tags = [
                CategoryTag.objects.get_or_create(name=tag_name)[0]
                for tag_name in category_tag_names
            ]

            video, created = Video.objects.update_or_create(
                source_url=url,
                defaults={
                    "title": document.find(".entry-header").text(),
                    "body": document.find(".entry-content").text(),
                    "date_published": published_date,
                },
            )

            for tag in theme_tags:
                TaggedThemeVideoItem.objects.create(tag=tag, content_object=video)

            for tag in category_tags:
                TaggedCategoryVideoItem.objects.create(tag=tag, content_object=video)
