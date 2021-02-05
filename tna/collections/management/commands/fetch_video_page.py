from django.utils import timezone
from datetime import datetime

import requests
import requests_cache

from pyquery import PyQuery as pq

from django.core.management.base import BaseCommand

from ....home.models import HomePage
from ...models import (
    VideoPage,
    VideoIndexPage,
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
        home_page = HomePage.objects.get()

        try:
            video_index_page = VideoIndexPage.objects.get()
        except VideoIndexPage.DoesNotExist:
            video_index_page = VideoIndexPage(title="Videos")
            home_page.add_child(instance=video_index_page)

        for url in fetch_audo_page_urls():
            print(f"fetching {url}")

            page = requests.get(url).content
            document = pq(page)

            published_date_string = (
                document.find(".entry-meta").text().split("|")[0].strip()
            )
            published_date = datetime.strptime(published_date_string, DATEIME_FORMAT)
            published_date = timezone.make_aware(published_date)

            theme_tag_names = [a.text for a in document.find(".tags a")]
            theme_tags = [
                ThemeTag.objects.get_or_create(name=tag_name.title())[0]
                for tag_name in theme_tag_names
            ]

            category_tag_names = [
                t.strip()
                for t in document.find(".entry-meta").text().split("|")[2].split(",")
            ]
            category_tags = [
                CategoryTag.objects.get_or_create(name=tag_name.title())[0]
                for tag_name in category_tag_names
            ]

            try:
                video_page = VideoPage.objects.get(source_url=url)
            except VideoPage.DoesNotExist:
                video_page = VideoPage()

            video_page.source_url = url
            video_page.title = document.find(".entry-header").text()
            video_page.body = document.find(".entry-content").text()
            video_page.date_published = published_date

            if not video_page.id:
                video_index_page.add_child(instance=video_page)

            for tag in theme_tags:
                TaggedThemeVideoItem.objects.create(tag=tag, content_object=video_page)

            for tag in category_tags:
                TaggedCategoryVideoItem.objects.create(
                    tag=tag, content_object=video_page
                )
