from django.core.management.base import BaseCommand, CommandError
from stories2.models import Comment

class Command(BaseCommand):
    help = "Show comments"

    def handle(self, *args, **options):
        print("{} comments:".format(Comment.objects.count()))
        for c in Comment.objects.all():
            print("{:20} {:30} {:5} {:20} {:50}".format(c.pub_date, c.author.first_name + ' ' + c.author.last_name, 
                    "ANON" if c.anonymous else "NAMED", c.story.title, c.text))
