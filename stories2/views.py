from rest_framework import viewsets, status
from stories2.models import FeedEntry, Publication, Story, Topic, Category, Comment, CommentUpvote
from stories2.serializers import FeedSerializer, PublicationSerializer, StorySerializer, TopicSerializer, CategorySerializer, CommentSerializer, AuthTokenCommentSerializer, AuthTokenCommentUpvoteSerializer,AuthTokenCommentFlagSerializer
from stories2.custom_permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.decorators import detail_route
from rest_framework import mixins
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

class FeedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = FeedEntry.objects.all()
    serializer_class = FeedSerializer

class PublicationViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    "API endpoint allowing REST services for publications."
    queryset = Publication.objects.filter(active=True)
    serializer_class = PublicationSerializer
    permission_classes = (IsAdminOrReadOnly,)

class StoryViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    "API endpoint allowing REST services for stories."
    queryset = Story.objects.filter(active=True)
    serializer_class = StorySerializer
    permission_classes = (IsAdminOrReadOnly,)

class TopicViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    "API endpoint allowing REST services for topics."
    queryset = Topic.objects.filter(active=True)
    serializer_class = TopicSerializer
    permission_classes = (IsAdminOrReadOnly,)

class CategoryViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Category.objects.filter(story_count__gte=3)
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)

class CommentViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    "API endpoint for comments"
    permission_classes = (AllowAny,)
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET': 
            return CommentSerializer
        elif self.action == 'upvote':
            return AuthTokenCommentUpvoteSerializer
        elif self.action == 'flag':
            return AuthTokenCommentFlagSerializer
        else:
            return AuthTokenCommentSerializer

    @detail_route(methods=['post'])
    def upvote(self, request, pk):
        data = {"comment": pk, "auth_token": self.request.data['auth_token']}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @detail_route(methods=['post'])
    def flag(self, request, pk):
        data = {"comment": pk, "auth_token": self.request.data['auth_token']}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
