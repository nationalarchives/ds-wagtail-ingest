# Wagtail content ingest 

This project started as a proof-of-concept for `InsightPage` (née
`ContentHubPage`) to test on whether it's possible to generate a page using
external (to Wagtail) content.

Its main purpose now is to fetch and save external page content and make it
available to its Elasticseach index.

The indexed content is picked up by CIIM where it's used to populate related
content on details pages and results for interpretive searches.

## Getting started

### Create `.env`

Copy `.env.example` to `.env`

### Build Docker Containers

```
$ docker-compose build
```

### Initialise Docker Containers

```
$ docker-compose up -d
```

### Tail Docker Logs

```
$ docker-compose logs -f --tail 50
```

### Create Database Schema

```
$ docker-compose exec web poetry run python manage.py migrate
```

## Environment variables

### `TNA_SCRAPER_EMAIL`

Email address for `ds-wagtail` user with access to page content. 

### `TNA_SCRAPER_PASSWORD`

Password address for `ds-wagtail` user with access to page content.

### `TNA_SCRAPER_BASE_URL`

URL of the Etna `ds-wagtail` whose page content will be scraped.

## Commands

Due to this project starting as proof-of-concept, the scripts to fetch page data
are sparsely commented but should be fairly self-explanatory.

All scripts will create an new page instance if fetched for the first time, or
update an existing page. All page types are saved under a
`<ContentType>IndexPage` to keep the page tree organised

###  Fetch Blog Pages

Iterates over paginated blog posts
(<https://blog.nationalarchives.gov.uk/blogposts/>), fetches and saves: 

 - title
 - slug
 - source URL
 - tags 
 - body content
 - article published date

```
$ docker-compose exec web poetry run python manage.py fetch_blog_pages
```

###  Fetch Research Guide Pages

Iterates over research guides (<https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/>), fetches: 

 - title
 - slug
 - source URL
 - tags 
 - body content

```
$ docker-compose exec web poetry run python manage.py fetch_research_guide_pages
```

###  Fetch Insights Pages

Iterates over insights pages from private beta, fetches and saves:

 - title
 - slug
 - source URL
 - body content

Note: this content is  behind a login, `TNA_SCRAPER_EMAIL` and `TNA_SCRAPER_PASSWORD`
need to be populated with beta tester account credentials.

```
$ docker-compose exec web poetry run python manage.py fetch_insights_pages
```

###  Fetch Video Pages

Iterates over paginated video pages
(<https://media.nationalarchives.gov.uk/index.php/category/video/>), fetches and
saves:

 - title
 - slug
 - source URL
 - body content
 - article published date
 - tags 

```
$ docker-compose exec web poetry run python manage.py fetch_video_pages
```

###  Fetch Audio Pages

Iterates over paginated audio pages
(<https://media.nationalarchives.gov.uk/index.php/category/audio/>), fetches and
saves:

 - title
 - slug
 - source URL
 - body content
 - article published date
 - tags 

```
$ docker-compose exec web poetry run python manage.py fetch_audio_pages
```

###  Fetch Learning Resource Pages

Iterates over learning resources listed here https://www.nationalarchives.gov.uk/education/sessions-and-resources/, fetches and saves:

 - title
 - sub title
 - slug
 - source URL
 - body content
 - tags 
 - suggested inquiry question
 - potential activities

```
$ docker-compose exec web poetry run python manage.py fetch_learning_resource_pages
```

###  Fetch Collection Results (Highlights) Pages

Iterates over collection results pages from private beta, fetches and saves:

 - title
 - slug
 - source URL
 - body content

Note: this content is  behind a login, `TNA_SCRAPER_EMAIL` and `TNA_SCRAPER_PASSWORD`
need to be populated with beta tester account credentials.

```
$ docker-compose exec web poetry run python manage.py fetch_results_pages
```

###  Fetch Exhibition Pages

Iterates over exhibition pages listed here https://www.nationalarchives.gov.uk/online-exhibitions/?sorted-by=a-z-by-title

Note: this isn't run nightly. Exhibition pagse are extremely difficult to
parse due to inconsistencies in page layouts.

 - title
 - slug
 - source URL
 - description

```
$ docker-compose exec web poetry run python manage.py fetch_exhibition_pages
```

## Caching

Some scripts employ caching using
[`requests_cache`](https://requests-cache.readthedocs.io/en/stable/) to speed up
runs during development. 

Technically, caching is also used in production however fetching fresh content
shouldn't be an issue due to platform.sh routinely clearing `/tmp/`

This may present issues on other environments though. If updated content isn't
being fetched, this would be the first place to look.
