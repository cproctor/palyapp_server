from rest_framework import viewsets, status
from stories.models import Publication, Story, Category, Comment
from stories.serializers import PublicationSerializer, StorySerializer, CategorySerializer, CommentSerializer, MaskedCommentSerializer, AuthorDetailCommentSerializer
from stories.custom_permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

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

class CategoryViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)

class CommentViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    "API endpoint for comments"
    permission_classes = (IsAuthenticated, IsAuthorOrAdminOrReadOnly)
    queryset = Comment.objects.all()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            if self.request.user.is_superuser:
                return AuthorDetailCommentSerializer
            else:
                return MaskedCommentSerializer
        else:
            return CommentSerializer
