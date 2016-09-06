from django.db import models
from django.utils.timezone import now
from datetime import datetime
import os

def s3_image_upload(instance, filename):
    "Generates a path name for an image to upload"
    filename_base, filename_ext = os.path.splitext(filename)
    return "images/{}{}".format(
        now().strftime("%Y%m%d%H%M%S"),
        filename_ext.lower()
    )

class Publication(models.Model):
    "Represents a Paly publication such as Campanile"

    def __str__(self):
        return self.name

    name = models.CharField(max_length=100)
    url = models.URLField()
    feed_url = models.URLField()
    logo = models.ImageField(upload_to=s3_image_upload)
    last_update = models.DateTimeField(default=datetime(1900, 1, 1))
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Story(models.Model):
    "Represents a story published by a publication"
    title = models.CharField(max_length=200)
    publisher = models.ForeignKey(Publication, related_name='stories')
    pub_date = models.DateTimeField()
    pub_id = models.IntegerField()
    authors = models.TextField() # To keep things simple, we will not have an authors object.
    categories = models.ManyToManyField(Category, related_name='stories')
    content = models.TextField() # Raw HTML
    text = models.TextField()

    def __str__(self):
        return "{} ({}; {}; {})".format(self.title, self.authors, self.publisher, self.pub_date.strftime("%m/%d/%y"))

    class Meta:
        ordering = ('publisher', 'pub_date')

class StoryImage(models.Model):
    story = models.ForeignKey(Story)
    image = models.ImageField(upload_to=s3_image_upload)
    caption = models.TextField(blank=True)
    sequence = models.IntegerField()
    # Add a resized version

class Comment(models.Model):
    author = models.ForeignKey('auth.User', related_name="comments")
    story = models.ForeignKey(Story, related_name="comments")
    text = models.TextField()
    anonymous = models.BooleanField(default=False)

    def __str__(self):
        return '"{}" (user {} on story {}{})'.format(
            self.text,
            self.author.id,
            self.story.id,
            "; anonymous" if self.anonymous else ""
        )

    def masked_author(self):
        return self.author if not self.anonymous else None
