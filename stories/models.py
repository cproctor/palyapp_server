from django.db import models
from django.utils.timezone import now
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
    
class Story(models.Model):
    "Represents a story published by a publication"
    title = models.CharField(max_length=200)
    publisher = models.ForeignKey(Publication)
    pub_date = models.DateTimeField()
    authors = models.TextField() # To keep things simple, we will not have an authors object.
    image = models.ImageField(upload_to=s3_image_upload)
    caption = models.TextField()
    content = models.TextField() # Not sure yet whether we'll want to store story content as HTML or plain text
