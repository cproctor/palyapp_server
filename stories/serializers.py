from rest_framework import serializers
from stories.models import Publication, Story, Category

class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = ('name', 'url', 'feed_url', 'logo', 'stories')
        depth = 1

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ('title', 'publisher', 'pub_date', 'authors', 'content', 'text', 'categories')
        depth = 1

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'stories')
        depth = 1
