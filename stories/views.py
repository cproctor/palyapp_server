from rest_framework import viewsets
from stories.models import Publication, Story
from stories.serializers import PublicationSerializer, StorySerializer

class PublicationViewSet(viewsets.ModelViewSet):
    "API endpoint allowing REST services for publications."
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer

class StoryViewSet(viewsets.ModelViewSet):
    "API endpoint allowing REST services for stories."
    queryset = Story.objects.all()
    serializer_class = StorySerializer
