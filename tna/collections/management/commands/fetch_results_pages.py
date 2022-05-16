import os
from django.conf import settings
from django.core.management.base import BaseCommand

import requests
import traceback

from pyquery import PyQuery as pq

from ....home.models import HomePage
from ...models import ResultsIndexPage, ResultsPage

session = requests.Session()

BASE_URL = os.getenv("BASE_URL")
LOGIN_URL = f"{BASE_URL}/accounts/login/"
INDEX_PAGE_URL = f"{BASE_URL}/explore-the-collection/"


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


def fetch_and_find_links(url, selector):
    response = session.get(url)
    document = pq(response.content)
    yield from document.find(selector)


def fetch_urls():
    # Fetch ExplorerIndexPage and find links to Topic/TimePeriod ExplorerPage
    for a in fetch_and_find_links(INDEX_PAGE_URL, ".card-group-promo__card-heading a"):
        # Fetch Topic/TimePeriod ExplorerPage and find links to Sub Topic/TimePeriod explorer page
        url = f"{BASE_URL}{a.attrib['href']}"
        for explorer_index_a in fetch_and_find_links(
            url, "a.card-group-secondary-nav__image-link"
        ):
            # Fetch Sub Topic/TimePeriod explorer page and find ResultsPage links
            explorer_page_url = f"{BASE_URL}{explorer_index_a.attrib['href']}"
            for results_page_a in fetch_and_find_links(
                explorer_page_url,
                "#analytics-collection-highlights a.card-group-secondary-nav__image-link",
            ):
                yield f"{BASE_URL}{results_page_a.attrib['href']}"


def fetch_page_data(url):
    slug = url.split("/")[-2]

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
        num_urls_updated = 0
        num_urls_errored = 0
        num_urls_fetched = 0

        home_page = HomePage.objects.get()

        results_index_page = ResultsIndexPage.objects.first()
        if not results_index_page:
            results_index_page = ResultsIndexPage(title="Highlights")
            home_page.add_child(instance=results_index_page)

        for url in fetch_urls():
            print(f"Processing {url}")
            num_urls_fetched += 1
            try:

                page_data = fetch_page_data(url)

                try:
                    results_page = ResultsPage.objects.get(source_url=url)
                except ResultsPage.DoesNotExist:
                    results_page = ResultsPage(source_url=url)

                results_page.slug = page_data["slug"]
                results_page.title = page_data["title"]
                results_page.body = page_data["body"]

                if not results_page.id:
                    results_index_page.add_child(instance=results_page)
                    num_urls_created += 1
                else:
                    results_page.save()
                    num_urls_updated += 1
            except Exception:
                print(f"Error in fetch_results_pages traceback= {traceback.format_exc()}")
                num_urls_errored += 1
     
        print(f"Number of urls fetched = {num_urls_fetched}")
        print(f"Number of urls created = {num_urls_created}")
        print(f"Number of urls updated = {num_urls_updated}")
        print(f"Number of urls errored = {num_urls_errored}")
