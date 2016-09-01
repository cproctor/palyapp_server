from rest_framework import serializers
from stories.models import Publication, Story

class PublicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Publication
        fields = ('name', 'url', 'feed_url', 'logo')

class StorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Story
        fields = ('title', 'publisher', 'pub_date', 'authors', 'image', 'caption', 'content')
