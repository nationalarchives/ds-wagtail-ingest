import requests
import requests_cache

from pyquery import PyQuery as pq

from django.core.management.base import BaseCommand

from ....home.models import HomePage
from ...models import (
    LearningResourcePage,
    LearningResourceIndexPage,
    TopicTag,
    TimePeriodTag,
    SuitableForTag,
    TaggedSuitableForLearningResourceTag,
    TaggedTimePeriodLearningResourceTag,
    TaggedTopicLearningResourceTag,
)

DATEIME_FORMAT = "%A %d %B %Y"

requests_cache.install_cache("learning_resources")


def fetch_learning_resource_page_links():
    base_url = f"https://www.nationalarchives.gov.uk/education/sessions-and-resources/"
    page = requests.get(base_url).content
    document = pq(page)

    links = document.find("#index div.resource-block > a")
    for a in links:
        yield a.attrib["href"]


# TODO parse out tags from document
TAG_HEADINGS = [
    "Suitable for:",
    "Time period:",
    "Curriculum topics:",
]


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        home_page = HomePage.objects.get()

        try:
            learning_resouce_index_page = LearningResourceIndexPage.objects.get()
        except LearningResourceIndexPage.DoesNotExist:
            learning_resouce_index_page = LearningResourceIndexPage(
                title="Learning Resources"
            )
            home_page.add_child(instance=learning_resouce_index_page)

        for url in fetch_learning_resource_page_links():
            print(f"fetching {url}")

            page = requests.get(url).content
            document = pq(page)

            tags = {}
            tag_type = ""
            for meta_data in document.find(
                "div.starts-at-full:nth-of-type(1) .pictorial-list p"
            ):
                try:
                    title = meta_data.find("strong")
                except AttributeError:
                    continue

                if title is None or title.text.strip() not in TAG_HEADINGS:
                    continue

                tag_type = title.text.strip()

                try:
                    tags[tag_type] = [a.text for a in meta_data.findall("a")]
                except (TypeError, AttributeError):
                    continue

            suggested_inquiry_question = ""
            for meta_data in document.find(
                "div.starts-at-full:nth-of-type(1) .pictorial-list p"
            ):
                try:
                    title = meta_data.find("strong")
                except AttributeError:
                    continue

                if (
                    title is None
                    or title.text.strip() != "Suggested inquiry questions:"
                ):
                    continue

                suggested_inquiry_question = (
                    meta_data.text_content()
                    .replace("Suggested inquiry questions:", "")
                    .strip()
                )

            potential_activities = ""
            for meta_data in document.find(
                "div.starts-at-full:nth-of-type(1) .pictorial-list p"
            ):
                try:
                    title = meta_data.find("strong")
                except AttributeError:
                    continue

                if title is None or title.text.strip() != "Potential activities:":
                    continue

                potential_activities = (
                    meta_data.text_content()
                    .replace("Potential activities:", "")
                    .strip()
                )

            title = document.find("h1").text()
            sub_title = document.find("h2").text()
            body = document.find(".article").text()

            if not body:
                print(f'Failed to parse {url}')
                continue

            try:
                learning_resource_page = LearningResourcePage.objects.get(
                    source_url=url
                )
            except LearningResourcePage.DoesNotExist:
                learning_resource_page = LearningResourcePage()

            learning_resource_page.source_url = url
            learning_resource_page.title = title
            learning_resource_page.sub_title = sub_title
            learning_resource_page.body = body
            learning_resource_page.suggested_inquiry_question = suggested_inquiry_question
            learning_resource_page.potential_activities = potential_activities

            if not learning_resource_page.id:
                learning_resouce_index_page.add_child(instance=learning_resource_page)
            learning_resource_page.save()

            try:
                for tag_name in tags["Suitable for:"]:
                    tag, _ = SuitableForTag.objects.get_or_create(name=tag_name)
                    TaggedSuitableForLearningResourceTag.objects.create(
                        tag=tag, content_object=learning_resource_page
                    )
            except KeyError:
                continue

            try:
                for tag_name in tags["Time period:"]:
                    tag, _ = TimePeriodTag.objects.get_or_create(name=tag_name)
                    TaggedTimePeriodLearningResourceTag.objects.create(
                        tag=tag, content_object=learning_resource_page
                    )
            except KeyError:
                continue

            try:
                for tag_name in tags["Curriculum topics:"]:
                    tag, _ = TopicTag.objects.get_or_create(name=tag_name)
                    TaggedTopicLearningResourceTag.objects.create(
                        tag=tag, content_object=learning_resource_page
                    )
            except KeyError:
                continue
