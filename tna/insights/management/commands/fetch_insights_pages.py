import re

from django.conf import settings
from django.core.management.base import BaseCommand

import requests
import traceback

from pyquery import PyQuery as pq

from ....home.models import HomePage
from ...models import InsightsIndexPage, InsightsPage

session = requests.Session()

LOGIN_URL = f"{settings.TNA_SCRAPER_BASE_URL}/accounts/login/"
INSIGHTS_INDEX_PAGE_URL = f"{settings.TNA_SCRAPER_BASE_URL}/insight-pages/"


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
        yield f'{settings.TNA_SCRAPER_BASE_URL}{a.attrib["href"]}'


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
        num_urls_created = 0
        num_urls_errored = 0
        num_urls_fetched = 0

        home_page = HomePage.objects.get()

        # In order update with latest changes CRUD made by the editor
        # or, since id for same data may be different accorss environments
        # Perform full-refresh
        InsightsIndexPage.objects.all().delete()

        insights_index_page = InsightsIndexPage.objects.first()
        if not insights_index_page:
            insights_index_page = InsightsIndexPage(title="Insights")
            home_page.add_child(instance=insights_index_page)

        for url in set(fetch_urls()):
            print(f"fetching {url}")
            num_urls_fetched += 1
            try:
                page_data = fetch_page_data(url)
                insights_index_page.add_child(instance=InsightsPage(
                    source_url=url,
                    title=page_data["title"],
                    body=page_data["body"],
                ))
                num_urls_created += 1
            except Exception as e:
                print(f"Error in fetch_insights_pages traceback= {traceback.format_exc()}")
                num_urls_errored += 1

        print(f"Number of urls fetched = {num_urls_fetched}")
        print(f"Number of urls created = {num_urls_created}")
        print(f"Number of urls errored = {num_urls_errored}")
