from rest_framework import serializers
from stories2.models import FeedEntry, Publication, Story, Topic, Category, Comment, StoryImage, CommentUpvote
from profiles2.models import Profile
from profiles2.serializers import AuthTokenUserSerializer
from versatileimagefield.serializers import VersatileImageFieldSerializer
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.http import Http404
from datetime import datetime

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

class FeedSerializer(serializers.ModelSerializer):
    content_type = serializers.SerializerMethodField()

    def get_content_type(self, obj):
        return obj.__class__.__name__

    class Meta:
        model = FeedEntry
        fields = ('id', 'content_type')

class FeedEntrySerializer(serializers.ModelSerializer):
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_like_count(self, obj):
        return obj.likes.count()

class StorySerializer(FeedEntrySerializer):
    images = StoryImageSerializer(many=True, read_only=True)
    flat_image_urls = serializers.SerializerMethodField()

    def get_flat_image_urls(self, obj):
        return [i.image.url for i in obj.images.all()]

    class Meta:
        model = Story
        fields = ('id', 'title', 'weight', 'publisher', 'pub_id', 'pub_date', 'authors', 
                'comment_count', 'content', 'text', 'images', 'flat_image_urls', 'categories')

class TopicSerializer(FeedEntrySerializer):
    class Meta: 
        model = Topic
        fields = ('id', 'title', 'weight', 'pub_date', 'stories', 'comment_count', 'like_count')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'stories', 'story_count')
        read_only_fields = ('story_count',)

class CommentSerializer(serializers.ModelSerializer):
    "A comment serializer"
    upvotes = serializers.SerializerMethodField()

    def get_upvotes(self, obj):
        return obj.upvotes.count()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'story', 'topic', 'text', 'pub_date', 'upvotes', 'promoted')

class AuthTokenCommentSerializer(serializers.Serializer):
    "A comment serializer which requires auth_tokens for destrictive actions"
    auth_token = serializers.CharField(max_length=100, write_only=True)
    story = serializers.PrimaryKeyRelatedField(queryset=Story.objects.all(), allow_null=True)
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), allow_null=True)
    text = serializers.CharField(trim_whitespace=True)

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("Comment text must not be empty")
        return value

    def validate(self, data):
        try:
            profile = Profile.objects.get(auth_token=data['auth_token'])
        except Profile.DoesNotExist:
            raise serializers.ValidationError("Invalid auth token")

        if data['story'] is None and data['topic'] is None:
            raise serializers.ValidationError("Comments must have a story or a topic")
        if not (data['story'] is None or data['topic'] is None):
            raise serializers.ValidationError("Comments must not have a story and a topic")
        return data

    def create(self, validated_data):
        profile = Profile.objects.get(auth_token=validated_data['auth_token'])
        comment = Comment(
            author = profile.user,
            story = get_object_or_404(Story, pk=validated_data['story']) if validated_data['story'] else None,
            topic = get_object_or_404(Topic, pk=validated_data['topic']) if validated_data['topic'] else None,
            text = validated_data['text'],
            pub_date = datetime.now()
        )
        comment.save()
        return comment

class AuthTokenCommentUpvoteSerializer(AuthTokenUserSerializer):
    "Translates an auth token into a CommentUpvote"
    comment = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all())

    def validate(self, data):
        comment = data['comment']
        if comment.upvotes.filter(author__profile__auth_token=data['auth_token']).exists():
           raise serializers.ValidationError("User has already upvoted this comment") 
        if hasattr(comment.author, 'profile') and comment.author.profile.auth_token == validated_data['auth_token']:
            raise serializers.ValidationError("Users may not upvote their own comments")
        return data

    def create(self, validated_data):
        upvote = CommentUpvote(
            author=Profile.objects.get(auth_token=validated_data['auth_token']).user,
            comment=validated_data['comment']
        )
        upvote.save()
        return upvote
