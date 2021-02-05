from django.utils import timezone
from datetime import datetime

import requests
import requests_cache

from pyquery import PyQuery as pq

from django.core.management.base import BaseCommand

from ....home.models import HomePage
from ...models import (
    AudioPage,
    AudioIndexPage,
    CategoryTag,
    ThemeTag,
    TaggedCategoryAudioItem,
    TaggedThemeAudioItem,
)

DATEIME_FORMAT = "%A %d %B %Y"

requests_cache.install_cache("Audio")


def fetch_audo_page_urls():
    for i in range(1, 54):
        base_url = (
            f"https://media.nationalarchives.gov.uk/index.php/category/audio/page/{i}/"
        )
        page = requests.get(base_url).content
        document = pq(page)

        for a in document.find("a.content-card"):
            yield a.attrib["href"]


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        home_page = HomePage.objects.get()

        try:
            audio_index_page = AudioIndexPage.objects.get()
        except AudioIndexPage.DoesNotExist:
            audio_index_page = AudioIndexPage(title="Audio Pages")
            home_page.add_child(instance=audio_index_page)

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
                audio_page = AudioPage.objects.get(source_url=url)
            except AudioPage.DoesNotExist:
                audio_page = AudioPage()

            audio_page.source_url=url
            audio_page.title=document.find(".entry-header").text()
            audio_page.body=document.find(".entry-content").text()
            audio_page.date_published=published_date

            if not audio_page.id:
                audio_index_page.add_child(instance=audio_page)

            for tag in theme_tags:
                TaggedThemeAudioItem.objects.create(tag=tag, content_object=audio_page)

            for tag in category_tags:
                TaggedCategoryAudioItem.objects.create(tag=tag, content_object=audio_page)
