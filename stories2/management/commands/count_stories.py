from django.core.management.base import BaseCommand, CommandError
from stories.models import Story, Category

class Command(BaseCommand):
    help = "Update the count of number of stories for each category"

    def handle(self, *args, **options):
        for category in Category.objects.all():
            category.story_count = category.stories.count()
            category.save()
