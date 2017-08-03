from django.db import models
from django.dispatch import receiver
from django.utils.timezone import now
from datetime import datetime
from versatileimagefield.fields import VersatileImageField
from versatileimagefield.placeholder import OnStoragePlaceholderImage
from versatileimagefield.image_warmer import VersatileImageFieldWarmer
import os
from django.core import files
import requests
import tempfile

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
    story_count = models.IntegerField("Story Count", default=0)

    def __str__(self):
        return self.name
    
class Story(models.Model):
    "Represents a story published by a publication"
    title = models.CharField('Title', max_length=200)
    publisher = models.ForeignKey(Publication, related_name='stories')
    pub_date = models.DateTimeField('Date published')
    pub_id = models.IntegerField('Publication ID')
    authors = models.TextField('Authors') # To keep things simple, we will not have an authors object.
    categories = models.ManyToManyField(Category, related_name='stories')
    content = models.TextField('Raw Content') # Raw HTML
    text = models.TextField('Text Content')
    active = models.BooleanField('Active', default=True)

    def ios_deeplink(self):
        return "paly://story/{}".format(self.id)

    def __str__(self):
        return "{} ({}; {}; {})".format(self.title, self.authors, self.publisher, self.pub_date.strftime("%m/%d/%y"))

    class Meta:
        ordering = ('publisher', 'pub_date')

class StoryImage(models.Model):
    story = models.ForeignKey(Story, related_name='images')
    image = VersatileImageField('Image', 
        upload_to=s3_image_upload, blank=True,
        placeholder_image=OnStoragePlaceholderImage(
            path='images/paly.jpg'
        )
    )
    sequence = models.IntegerField()

    @classmethod
    def from_url(cls, url, **kwargs):
        response = requests.get(url, stream=True)
        if response.status_code != requests.codes.ok:
            raise IOError("Status code for {} was {}.".format(url, response.status_code))
        f = tempfile.NamedTemporaryFile()
        for block in response.iter_content(1024 * 8):
            if not block:
                break
            f.write(block)
        return StoryImage(image=files.File(f), **kwargs)

@receiver(models.signals.post_save, sender=StoryImage)
def warm_story_images_images(sender, instance, **kwargs):
    """Ensures story images are created post-save"""
    story_img_warmer = VersatileImageFieldWarmer(
        instance_or_queryset=instance,
        rendition_key_set='story_image',
        image_attr='image'
    )
    num_created, failed_to_create = story_img_warmer.warm()

class Comment(models.Model):
    author = models.ForeignKey('auth.User', related_name="comments_v1")
    story = models.ForeignKey(Story, related_name="comments")
    text = models.TextField()
    pub_date = models.DateTimeField()
    anonymous = models.BooleanField(default=False)

    def __str__(self):
        return '"{}" (user {} on story {} at {}{})'.format(
            self.text,
            self.author.id,
            self.story.id,
            self.pub_date.strftime("%m/%d/%y"),
            "; anonymous" if self.anonymous else ""
        )

    def masked_author(self):
        return self.author if not self.anonymous else None

@receiver(models.signals.post_save, sender=Comment)
def notify_discussion_participants(sender, instance, **kwargs):
    """Send a push notification to all other commenters when a comment is created"""
    authors = [c.author for c in instance.story.comments.all() if c.author != instance.author]
    devices = APNSDevice.objects.filter(user__in=authors)
    devices.send_message(None,  extra={
        "aps":{
            "alert": "New comment",
            "sound": "default",
            "badge": 1,
            "deeplink": instance.story.ios_deeplink()
        }
    })

class CommentUpvote(models.Model):
    "Records a single user's upvote of a single comment"
    comment = models.ForeignKey(Comment, related_name="upvotes")
    author = models.ForeignKey('auth.User', related_name="upvotes_v1")

    def clean(self):
        if self.comment.author == self.author:
            raise ValidationError("Users may not upvote their own comments")

    class Meta:
        unique_together = (('comment', 'author'),)
    












