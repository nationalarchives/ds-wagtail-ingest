from django.utils import timezone
from datetime import datetime

import requests
import requests_cache

from pyquery import PyQuery as pq

from django.core.management.base import BaseCommand

from ....home.models import HomePage
from ....collections.models import (
    CategoryTag,
    ThemeTag,
)
from ...models import (
    AudioPage,
    AudioIndexPage,
    TaggedCategoryAudioItem,
    TaggedThemeAudioItem,
)

DATEIME_FORMAT = "%A %d %B %Y"

requests_cache.install_cache("Audio")


def fetch_audio_page_urls():
    for i in range(1, 54):
        base_url = (
            f"https://media.nationalarchives.gov.uk/index.php/category/audio/page/{i}/"
        )
        page = requests.get(base_url).content
        document = pq(page)

        for a in document.find("a.content-card"):
            yield a.attrib["href"]


def fetch_audio_page_data(url):
    page = requests.get(url).content
    document = pq(page)

    published_date_string = document.find(".entry-meta").text().split("|")[0].strip()
    date_published = datetime.strptime(published_date_string, DATEIME_FORMAT)
    date_published = timezone.make_aware(date_published)

    return {
        "title": document.find(".entry-header").text(),
        "body": document.find(".entry-content").text(),
        "date_published": date_published,
        "theme_tag_names": [a.text for a in document.find(".tags a")],
        "category_tag_names": [
            t.strip()
            for t in document.find(".entry-meta").text().split("|")[2].split(",")
        ],
    }


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        home_page = HomePage.objects.get()

        try:
            audio_index_page = AudioIndexPage.objects.get()
        except AudioIndexPage.DoesNotExist:
            audio_index_page = AudioIndexPage(title="Audio Pages")
            home_page.add_child(instance=audio_index_page)

        for url in fetch_audio_page_urls():
            page_data = fetch_audio_page_data(url)
            print(f"fetching {url}")

            theme_tags = [
                ThemeTag.objects.get_or_create(name=tag_name.title())[0]
                for tag_name in page_data["theme_tag_names"]
            ]

            category_tags = [
                CategoryTag.objects.get_or_create(name=tag_name.title())[0]
                for tag_name in page_data["category_tag_names"]
            ]

            try:
                audio_page = AudioPage.objects.get(source_url=url)
            except AudioPage.DoesNotExist:
                audio_page = AudioPage(source_url=url)

            audio_page.title = page_data["title"]
            audio_page.body = page_data["body"]
            audio_page.date_published = page_data["date_published"]

            if not audio_page.id:
                audio_index_page.add_child(instance=audio_page)
            else:
                audio_page.save()

            for tag in theme_tags:
                TaggedThemeAudioItem.objects.create(tag=tag, content_object=audio_page)

            for tag in category_tags:
                TaggedCategoryAudioItem.objects.create(
                    tag=tag, content_object=audio_page
                )
