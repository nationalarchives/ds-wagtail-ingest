from django.utils import timezone
from datetime import datetime

import requests
import requests_cache

from pyquery import PyQuery as pq

from django.core.management.base import BaseCommand

from ....home.models import HomePage
from ....collections.models import CategoryTag, ThemeTag
from ...models import AudioPage, AudioIndexPage

DATEIME_FORMAT = "%A %d %B %Y"

requests_cache.install_cache("/tmp/audio")


def fetch_page_urls():
    # The audio index currently contains ~52 pages. In theory, a while True would work
    # here but I don't feel comfortable potentially scraping the TNA site indefinitely
    for i in range(0, 60):
        base_url = (
            f"https://media.nationalarchives.gov.uk/index.php/category/audio/page/{i}/"
        )
        response = requests.get(base_url, allow_redirects=False)

        # The index pages respond with a redirect instead of a 404 if a page isn't found.
        if response.status_code == 301 and "PageNotFound" in response.headers.get(
            "Location", ""
        ):
            return

        page = response.content
        document = pq(page)

        for a in document.find("a.content-card"):
            yield a.attrib["href"]


def fetch_page_data(url):
    page = requests.get(url).content
    document = pq(page)

    published_date_string = document.find(".entry-meta").text().split("|")[0].strip()
    date_published = datetime.strptime(published_date_string, DATEIME_FORMAT)
    date_published = timezone.make_aware(date_published)

    return {
        "title": document.find(".entry-header").text(),
        "body": document.find(".entry-content").html(),
        "date_published": date_published,
        "theme_tag_names": [a.text.strip().title() for a in document.find(".tags a")],
        "category_tag_names": [
            t.strip().title()
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

        for url in fetch_page_urls():
            print(f"fetching {url}")

            page_data = fetch_page_data(url)

            try:
                page = AudioPage.objects.get(source_url=url)
            except AudioPage.DoesNotExist:
                page = AudioPage(source_url=url)

            page.title = page_data["title"]
            page.body = page_data["body"]
            page.date_published = page_data["date_published"]

            for name in page_data["theme_tag_names"]:
                if not page.theme_tags.filter(name=name).exists():
                    tag, _ = ThemeTag.objects.get_or_create(name=name)
                    page.theme_tags.add(tag)

            for name in page_data["category_tag_names"]:
                if not page.content_tags.filter(name=name).exists():
                    tag, _ = CategoryTag.objects.get_or_create(name=name)
                    page.content_tags.add(tag)

            if not page.id:
                audio_index_page.add_child(instance=page)
            else:
                page.save()
