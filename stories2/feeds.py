from feedparser import parse
from time import mktime
from datetime import datetime
import re
import pytz
from bs4 import BeautifulSoup
import requests
import logging


# Defines classes for feeds and feed entries for different publications

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
        self.soup = None

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
        if not self.soup:
            response = requests.get(self.story_url())
            if response.status_code != requests.codes.ok:
                raise IOError("Response status code was {}.".format(response.status_code))
            self.soup = BeautifulSoup(response.content, 'html.parser')
        return self.soup

    def image_urls(self):
        soup = self.scrape()
        urls = []
        for containerKW in self.IMAGE_CONTAINERS:
            container = soup.find(**containerKW)
            if container: 
                for img in container.findAll('img'):
                    url = fix_url_scheme(img['src'])
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
        for index in self.pages_to_scan:
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
        {'class_': 'story-content'},
        {'class_': 'newsstand-blog-single-content'}
    ]

class PalyVikingFeedEntry(WordpressFeedEntry):
    IMAGE_CONTAINERS = [
        {'class_': 'photowrap'},
        {'class_': 'phototop'},
    ]
    def pub_id(self):
        result = re.search("p=(\d+)", self.parsedEntry['guid'])
        return int(result.group(1))

class PalyCMagFeedEntry(WordpressFeedEntry):
    IMAGE_CONTAINERS = [
        {'class_': 'postarea'}
    ]
    def pub_id(self):
        result = re.search("p=(\d+)", self.parsedEntry['guid'])
        return int(result.group(1))

class PalyVerdeFeedEntry(WordpressFeedEntry):
    IMAGE_CONTAINERS = [
        {'class_': 'cb-entry-content'},
        {'class_': 'cb-featured-image'},
        {'id': 'cb-gallery-post'},
    ]
    def pub_id(self):
        result = re.search("p=(\d+)", self.parsedEntry['guid'])
        return int(result.group(1))

    def content(self):
        soup = self.scrape()
        return str(soup.section)
        
class PalyCampanileFeedEntry(WordpressFeedEntry):
    IMAGE_CONTAINERS = [
        {'id': 'cb-standard-featured'},
    ]
    def pub_id(self):
        result = re.search("p=(\d+)", self.parsedEntry['guid'])
        return int(result.group(1))

class PalyAgoraFeedEntry(WordpressFeedEntry):
    IMAGE_CONTAINERS = [
        {'name': 'article'}
    ]
    def pub_id(self):
        result = re.search("p=(\d+)", self.parsedEntry['guid'])
        return int(result.group(1))

class PalyVoiceFeed(WordpressFeed):
    feedItemClass = PalyVoiceFeedEntry

class PalyVikingFeed(WordpressFeed):
    feedItemClass = PalyVikingFeedEntry
     
class PalyVerdeFeed(WordpressFeed):
    feedItemClass = PalyVerdeFeedEntry

class PalyCMagFeed(WordpressFeed):
    feedItemClass = PalyCMagFeedEntry

class PalyCampanileFeed(WordpressFeed):
    feedItemClass = PalyCampanileFeedEntry

class PalyAgoraFeed(WordpressFeed):
    feedItemClass = PalyAgoraFeedEntry
    def get_feed_page(self, index):
        return parse("{}&paged={}".format(self.url, index))

# Publication to parser mapping
parsers = {
    "Campanile": PalyCampanileFeed,
    "Voice": PalyVoiceFeed,
    "Viking": PalyVikingFeed,
    "C Magazine": PalyCMagFeed,
    "Verde": PalyVerdeFeed,
    "Agora": PalyAgoraFeed
}

