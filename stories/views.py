from rest_framework import viewsets
from stories.models import Publication, Story, Category
from stories.serializers import PublicationSerializer, StorySerializer, CategorySerializer

class PublicationViewSet(viewsets.ModelViewSet):
    "API endpoint allowing REST services for publications."
    queryset = Publication.objects.filter(active=True)
    serializer_class = PublicationSerializer

class StoryViewSet(viewsets.ModelViewSet):
    "API endpoint allowing REST services for stories."
    queryset = Story.objects.all()
    serializer_class = StorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
