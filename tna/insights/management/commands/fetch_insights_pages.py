import re

from django.conf import settings
from django.core.management.base import BaseCommand

import requests

from pyquery import PyQuery as pq

from ....home.models import HomePage
from ...models import InsightsIndexPage, InsightsPage

session = requests.Session()

LOGIN_URL = "https://beta.nationalarchives.gov.uk/accounts/login/"
INSIGHTS_INDEX_PAGE_URL = "https://beta.nationalarchives.gov.uk/insight-pages/"


def login():
    session.get(LOGIN_URL)
    session.post(
        LOGIN_URL,
        data={
            "csrfmiddlewaretoken": session.cookies["csrftoken"],
            "login": settings.TNA_SCRAPER_EMAIL,
            "password": settings.TNA_SCRAPER_PASSWORD,
        },
        headers={"Referer": LOGIN_URL},
    )


def fetch_urls():
    response = session.get(INSIGHTS_INDEX_PAGE_URL)

    page = response.content
    document = pq(page)

    for a in document.find("a.card-group-secondary-nav__image-link"):
        yield f'https://beta.nationalarchives.gov.uk{a.attrib["href"]}'


def fetch_page_data(url):
    slug = re.match(f"^{INSIGHTS_INDEX_PAGE_URL}(.*)/$", url)[1]

    page = session.get(url).content
    document = pq(page)

    return {
        "slug": slug,
        "title": document.find("h1").text(),
        "body": document.find("#maincontent").html(),
    }


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        login()

        home_page = HomePage.objects.get()

        insights_index_page = InsightsIndexPage.objects.first()
        if not insights_index_page:
            insights_index_page = InsightsIndexPage(title="Insights")
            home_page.add_child(instance=insights_index_page)

        for url in fetch_urls():
            print(f"fetching {url}")

            page_data = fetch_page_data(url)

            try:
                insights_page = InsightsPage.objects.get(source_url=url)
            except InsightsPage.DoesNotExist:
                insights_page = InsightsPage(source_url=url)

            insights_page.slug = page_data["slug"]
            insights_page.title = page_data["title"]
            insights_page.body = page_data["body"]

            if not insights_page.id:
                insights_index_page.add_child(instance=insights_page)
            else:
                insights_page.save()
