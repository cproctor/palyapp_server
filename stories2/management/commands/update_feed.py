from django.core.management.base import BaseCommand, CommandError
from stories2.models import FeedEntry

class Command(BaseCommand):
    help = "Update the weight of all feed entries, based on likes, comments and age."

    def handle(self, *args, **options):
        for fe in FeedEntry.objects.all():
            fe.update_weight()
            fe.save()
