# load_publications.py
# Defines a django management command to load publication data. Should only be needed on initial install.
# Reference: https://docs.djangoproject.com/en/1.10/howto/custom-management-commands/

from django.core.management.base import BaseCommand, CommandError
from stories.models import Publication

class Command(BaseCommand):
    help = "Load the basic information about the publications into the database"

    def handle(self, *args, **options):
        pass # Come back to this once rest-framework is in plae and s3 functionality confirmed.
        
