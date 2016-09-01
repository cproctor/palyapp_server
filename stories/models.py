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

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
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

class StoryImage(models.Model):
    story = models.ForeignKey(Story)
    image = models.ImageField(upload_to=s3_image_upload)
    caption = models.TextField(blank=True)
    sequence = models.IntegerField()
    # Add a resized version
