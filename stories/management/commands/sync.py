from django.core.management.base import BaseCommand, CommandError
from django.core import files
from feedparser import parse
from stories.models import Publication, Story, Category
from time import mktime
from datetime import datetime
import re
import pytz
from bs4 import BeautifulSoup
import requests
import tempfile

# Should work for Wordpress feeds, which are all we need.
# Not robust for others.

PAGES_TO_SCAN = 3

def get_pub_id(entry):
    if entry.get('post-id'):
        return int(entry['post-id'])
    elif entry.get('guid'):
        result = re.search("p=(\d+)", entry['guid'])
        if result:
            return int(result.group(1))
    raise ValueError("Could not parse publication ID for entry: {}".format(entry))

def get_categories(entry):
    if entry.get('tags'):
        return map(lambda tag: Category.objects.get_or_create(name=tag['term'])[0], entry['tags'])
    else:
        return []

def get_content(entry):
    if hasattr(entry, 'content'):
        return entry.content[0]['value']
    else:
        return ""

def get_story_url(entry):
    return entry.link

def get_primary_image_url(entry):
    response = requests.get(get_story_url(entry))
    if response.status_code != requests.codes.ok:
        return None
    soup = BeautifulSoup(response.content, 'html.parser')
    imageIdentifiers = [
        {'id': 'cb-standard-featured'}, # Campanile
        {'id': 'cb-featured-image'}, # Verde
        {'class_': 'permalinkphotobox'}, # Viking
        {'class_': 'story-content'} # Voice
    ]
    for identifier in imageIdentifiers:
        container = soup.find(**identifier)
        if container:
            img = container.find('img')
            if img:
                return img['src']

def get_primary_image(entry):
    "Download the primary image and return it as a temporary file"
    url = get_primary_image_url(entry)
    if url is None:
        return None
    response = requests.get(url, stream=True)
    if response.status_code != requests.codes.ok:
        return None
    f = tempfile.NamedTemporaryFile()
    for block in response.iter_content(1024 * 8):
        if not block:
            break
        f.write(block)
    return files.File(f)

def to_local_datetime(time_struct):
    "Converts a time struct to a datetime (via a timestamp), and then localizes to UTC"
    return pytz.UTC.localize(datetime.fromtimestamp(mktime(time_struct)))

class Command(BaseCommand):
    help = "Sync stories and publications with published feeds"

    def add_arguments(self, parser):
        parser.add_argument('--force', action="store_true", dest="force", default=False,
                help="Force updates even if the feed is not new")

    def handle(self, *args, **options):
        for pub in Publication.objects.filter(active=True).all():
            feed = parse(pub.feed_url)
            try:
                lastUpdate = to_local_datetime(feed.updated_parsed)
            except AttributeError:
                lastUpdate = None
            if options['force'] or lastUpdate is None or lastUpdate > pub.last_update:
                for page in range(1, PAGES_TO_SCAN + 1):
                    self.stdout.write(self.style.SUCCESS("- Syncing {}, Page {}".format(pub.name, page)))
                    feed = parse("{}?paged={}".format(pub.feed_url, page))
                    for entry in feed.entries:
                        pubDate = to_local_datetime(entry.published_parsed)
                        pubId = get_pub_id(entry)
                        try:
                            story = pub.stories.get(pub_id=pubId)
                            if options['force'] or pubDate > story.pub_date:
                                story.title = entry.title
                                story.pub_date = pubDate
                                story.authors = entry.author
                                story.content = entry.content[0]['value']
                                story.text = BeautifulSoup(story.content, 'html.parser').get_text()
                                story.image = get_primary_image(entry)
                                story.save()
                                story.categories.add(*get_categories(entry))
                                self.stdout.write(self.style.SUCCESS('  - Updated {}'.format(story.title)))
                        except Story.DoesNotExist:
                            story = Story(
                                title = entry.title,
                                publisher = pub,
                                pub_date = pubDate,
                                pub_id = pubId,
                                authors = entry.author,
                                content = get_content(entry),
                                image = get_primary_image(entry)
                            )
                            story.text = BeautifulSoup(story.content, 'html.parser').get_text()
                            story.save()
                            story.categories.add(*get_categories(entry))
                            self.stdout.write(self.style.SUCCESS('  - Created {}'.format(story.title)))
                pub.last_update = lastUpdate
                pub.save()
