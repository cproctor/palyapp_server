from django.core.management.base import BaseCommand, CommandError
from django.core import files
from feedparser import parse
from stories.models import Publication, Story, Category, StoryImage
from time import mktime
from datetime import datetime
import re
import pytz
from bs4 import BeautifulSoup
import requests
import tempfile
import logging

# Helpers

def to_local_datetime(time_struct):
    "Converts a time struct to a datetime (via a timestamp), and then localizes to UTC"
    return pytz.UTC.localize(datetime.fromtimestamp(mktime(time_struct)))

def fix_url_scheme(url, scheme="http"):
    if url.startswith("//"):
        return "{}:{}".format(scheme, url)
    else:
        return url

def filter_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

class WordpressFeedEntry:
    "Wraps a feedparser entry object with subclassable convenience methods"

    TAGS_KEY = 'tags'
    CONTENT_KEY = 'content'
    URL_KEY = 'link'
    IMAGE_CONTAINERS = [
        {'class_': 'story-content'}
    ]

    def __init__(self, parsedEntry, logger=logging):
        self.parsedEntry = parsedEntry
        self.logger = logger

    def pub_id(self):
        result = re.search("p=(\d+)", self.parsedEntry['guid'])
        return int(result.group(1))

    def pub_date(self):
        return to_local_datetime(self.parsedEntry.published_parsed)

    def title(self):
        return self.parsedEntry.title

    def authors(self):
        return self.parsedEntry.author
    
    def tags(self):
        return [tag['term'] for tag in self.parsedEntry.get(self.TAGS_KEY, [])]
    
    def content(self):
        if hasattr(self.parsedEntry, self.CONTENT_KEY):
            return getattr(self.parsedEntry, self.CONTENT_KEY)[0]['value']
        else:
            return ""

    def text(self):
        return BeautifulSoup(self.content(), 'html.parser').get_text()
    
    def story_url(self):
        return fix_url_scheme(getattr(self.parsedEntry, self.URL_KEY))
    
    def scrape(self):
        response = requests.get(self.story_url())
        if response.status_code != requests.codes.ok:
            raise IOError("Response status code was {}.".format(response.status_code))
        return BeautifulSoup(response.content, 'html.parser')

    def image_urls(self):
        soup = self.scrape()
        urls = []
        for containerKW in self.IMAGE_CONTAINERS:
            container = soup.find(**containerKW)
            if container: 
                for img in container.findAll('img'):
                    url = fix_url_scheme(img['src'])
                    self.logger.info("    - Image: {}".format(url))
                    urls.append(url)
        if not any(urls):
            self.logger.warn("    - No images found")
        return filter_duplicates(urls)

class WordpressFeed:
    feedItemClass = WordpressFeedEntry

    def __init__(self, name, url, pages_to_scan=3, logger=logging):
        self.name = name
        self.url = url
        self.parsedFeed = parse(url)
        self.pages_to_scan = pages_to_scan
        self.logger = logger

    def get_feed_page(self, index):
        return parse("{}?paged={}".format(self.url, index))

    def entries(self):
        for index in range(1, self.pages_to_scan + 1):
            self.logger.info("- Syncing {}, Page {}".format(self.name, index))
            feedPage = self.get_feed_page(index) 
            for entry in feedPage.entries:
                yield self.feedItemClass(entry, logger=self.logger)

    def last_update(self):
       try:
            return to_local_datetime(self.parsedFeed.updated_parsed)
       except AttributeError:
            return None

# Publication Subclasses

class PalyVoiceFeedEntry(WordpressFeedEntry):
    IMAGE_CONTAINERS = [
        {'class_': 'story-content'}
    ]

class PalyVoiceFeed(WordpressFeed):
    feedItemClass = PalyVoiceFeedEntry

class PalyVikingFeedEntry(WordpressFeedEntry):
    IMAGE_CONTAINERS = [
        {'class_': 'photowrap'},
        {'class_': 'phototop'},
    ]
    def pub_id(self):
        result = re.search("p=(\d+)", self.parsedEntry['guid'])
        return int(result.group(1))

class PalyVikingFeed(WordpressFeed):
    feedItemClass = PalyVikingFeedEntry
     
class PalyVerdeFeedEntry(WordpressFeedEntry):
    IMAGE_CONTAINERS = [
        {'class_': 'cb-entry-content'},
        {'class_': 'cb-featured-image'},
        {'id': 'cb-gallery-post'},
    ]
    def pub_id(self):
        result = re.search("p=(\d+)", self.parsedEntry['guid'])
        return int(result.group(1))

class PalyVerdeFeed(WordpressFeed):
    feedItemClass = PalyVerdeFeedEntry

class PalyCampanileFeedEntry(WordpressFeedEntry):
    IMAGE_CONTAINERS = [
        {'id': 'cb-standard-featured'},
    ]
    def pub_id(self):
        result = re.search("p=(\d+)", self.parsedEntry['guid'])
        return int(result.group(1))

class PalyCampanileFeed(WordpressFeed):
    feedItemClass = PalyCampanileFeedEntry

# Publication to parser mapping
parsers = {
    "Campanile": None,
    "Voice": PalyVoiceFeed,
    "Viking": PalyVikingFeed,
    "C Magazine": None,
    "Verde": PalyVerdeFeed
}

class CommandLogger:
    "Roughly emulates a Logger API, emitting in the style of Django management commands"
    def __init__(self, command):
        self.command = command
    def info(self, msg):
        self.command.stdout.write(self.command.style.SUCCESS(msg))
    def warn(self, msg):
        self.command.stdout.write(self.command.style.WARNING(msg))

class Command(BaseCommand):
    help = "Sync stories and publications with published feeds"

    def add_arguments(self, parser):
        parser.add_argument('--force', action="store_true", dest="force", default=False,
                help="Force updates even if the feed is not new")

    def handle(self, *args, **options):
        log = CommandLogger(self)
        for pub in Publication.objects.filter(active=True).all():
            feedClass = parsers.get(pub.name)
            if not feedClass:
                continue
            feed = feedClass(pub.name, pub.feed_url, logger=log, pages_to_scan=1)
            if options['force'] or feed.last_update() is None or feed.last_update() > pub.last_update:
                for entry in feed.entries():
                    try:
                        story = pub.stories.get(pub_id=entry.pub_id())
                        self.stdout.write(self.style.SUCCESS('  - Updating {}'.format(entry.title())))
                        if options['force'] or entry.pub_date() > story.pub_date:
                            story.title = entry.title()
                            story.pub_date = entry.pub_date()
                            story.authors = entry.authors()
                            story.content = entry.content()
                            story.text = entry.text()
                        else:
                            self.stdout.write(self.style.SUCCESS('  - No change to {}'.format(entry.title())))
                    except Story.DoesNotExist:
                        self.stdout.write(self.style.SUCCESS('  - Creating {}'.format(entry.title())))
                        story = Story(
                            title = entry.title(),
                            publisher = pub,
                            pub_date = entry.pub_date(),
                            pub_id = entry.pub_id(),
                            authors = entry.authors(),
                            content = entry.content(),
                            text = entry.text()
                        )
                    story.save()
                    for tag in entry.tags():
                        story.categories.add(Category.objects.get_or_create(name=tag)[0])
                    for url in entry.image_urls():
                        story.images.add(StoryImage.from_url(url, sequence=story.images.count()), bulk=False)
            pub.last_update = feed.last_update()
            pub.save()
