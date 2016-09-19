from django.core.management.base import BaseCommand, CommandError
from stories.models import Story

class Command(BaseCommand):
    help = "Drop all stories"

    def handle(self, *args, **options):
        for story in Story.objects.all():
            story.delete()
