from rest_framework import serializers
from stories.models import Publication, Story, Category, Comment, StoryImage
from versatileimagefield.serializers import VersatileImageFieldSerializer
from django.contrib.auth.models import User

class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = ('id', 'name', 'url', 'feed_url', 'logo', 'stories')
        read_only_fields = ('stories',)

class StoryImageSerializer(serializers.ModelSerializer):
    image = VersatileImageFieldSerializer(sizes='story_image')

    class Meta:
        model = StoryImage
        fields = ('image',)


class StorySerializer(serializers.ModelSerializer):
    images = StoryImageSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    def get_comment_count(self, obj):
        return obj.comments.count()

    class Meta:
        model = Story
        fields = ('id', 'title', 'publisher', 'pub_date', 'authors', 
                'comment_count', 'content', 'text', 'images', 'categories')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'stories', 'story_count')
        read_only_fields = ('story_count',)
        #depth = 1

class CommentAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name')

class CommentSerializer(serializers.ModelSerializer):
    "A full-power serializer for comments."
    upvotes = serializers.SerializerMethodField()

    def get_upvotes(self, obj):
        return obj.upvotes.count()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'story', 'text', 'pub_date', 'upvotes', 'anonymous')
        read_only_fields = ('votes',)

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

#class CommentUpvoteSerializer(serializers.ModelSerializer):
    #class Meta:
        #fields = ('comment', 'author')

