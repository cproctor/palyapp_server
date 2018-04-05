from django.core.management.base import BaseCommand, CommandError
from django.core import files
from stories2.models import Publication, Story, Category, StoryImage
from stories2.feeds import parsers

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
        parser.add_argument('--page', type=int, help="Specify which page of the feed should be parsed. Default is 1-3.")
        parser.add_argument('--pub', help="Specify which publication should be synced. Default is all.")

    def handle(self, *args, **options):
        log = CommandLogger(self)
        if options['pub'] is None:
            pubs = Publication.objects.filter(active=True).all()
        else:
            pubs = Publication.objects.filter(active=True, name=options['pub']).all()
            if len(pubs) == 0:
                log.warn("No publications selected")
        if options['page'] is None:
            pages = range(1, 4)
        else:
            pages = [options['page']]
        for pub in pubs:
            if not pub.active: 
                log.warn("  - Skipping {} because it is marked inactive.".format(pub.name))
                continue
            feedClass = parsers.get(pub.name)
            if not feedClass: 
                log.warn("  - Skipping {} because no feed class is implemented.".format(pub.name))
                continue
            feed = feedClass(pub.name, pub.feed_url, logger=log, pages_to_scan=pages)
            if not (
                options['force'] or 
                feed.last_update() is None or 
                feed.last_update() > pub.last_update
            ):
                log.warn("  - Skipping {} because there are no new changes.".format(pub.name))
                continue
            for entry in feed.entries():
                try:
                    story = pub.stories.get(pub_id=entry.pub_id())
                    if options['force'] or entry.pub_date() > story.pub_date:
                        self.stdout.write(self.style.SUCCESS('  - Updating {}'.format(entry.title())))
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
                    if story.images.filter(source_url=url).exists():
                        log.warn("    = Image already exists: {}".format(url))
                        continue
                    story.images.add(
                        StoryImage.from_url(url, sequence=story.images.count()), 
                        bulk=False
                    )
                    log.info("    = Image: {}".format(url))
            pub.last_update = feed.last_update()
            pub.save()
