from rest_framework import serializers
from stories.models import Publication, Story, Category, Comment
from versatileimagefield.serializers import VersatileImageFieldSerializer
from django.contrib.auth.models import User

class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = ('id', 'name', 'url', 'feed_url', 'logo', 'stories')
        read_only_fields = ('stories',)

class StorySerializer(serializers.ModelSerializer):
    image = VersatileImageFieldSerializer(sizes='story_image')

    class Meta:
        model = Story
        fields = ('id', 'title', 'publisher', 'pub_date', 'authors', 
                'content', 'text', 'image', 'categories')
        read_only_fields = ('image',)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'stories')
        #depth = 1

class CommentAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name')

class CommentSerializer(serializers.ModelSerializer):
    "A full-power serializer for comments."
    class Meta:
        model = Comment
        fields = ('id', 'author', 'story', 'text', 'pub_date', 'anonymous')

class AuthorDetailCommentSerializer(CommentSerializer):
    "A serializer which offers details of authorship, but which is therefore read-only for author"
    author = CommentAuthorSerializer(read_only=True)

class MaskedCommentSerializer(serializers.ModelSerializer):
    "A read-only serializer for comments which hides the authors of anonymous comments"
    author = CommentAuthorSerializer(read_only=True, source='masked_author')

    class Meta:
        model = Comment
        fields = ('id', 'author', 'story', 'text', 'pub_date', 'anonymous')
        read_only_fields = ('id', 'author', 'story', 'text', 'pub_date', 'anonymous')

