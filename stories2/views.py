from rest_framework import viewsets, status
from stories2.models import Publication, Story, Topic, Category, Comment, CommentUpvote
from stories2.serializers import PublicationSerializer, StorySerializer, TopicSerializer, CategorySerializer, CommentSerializer, MaskedCommentSerializer, AuthorDetailCommentSerializer
from stories2.custom_permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.decorators import detail_route
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

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

    @detail_route(methods=['post'])
    def upvote(self, request, pk):
        comment = self.get_object()
        upvote = CommentUpvote(comment=comment, author=request.user)
        try:
            upvote.full_clean()
            upvote.save()
            return Response({'status': 'comment upvote recorded'})
        except ValidationError as e:
            return Response(e.message_dict[NON_FIELD_ERRORS],
                            status=status.HTTP_400_BAD_REQUEST)
            
        



