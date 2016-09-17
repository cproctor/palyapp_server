"""palyapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework_extensions import routers
from stories import views
from profiles.views import Signup, UpdateAnalytics

router = routers.ExtendedDefaultRouter()
router.register('publications', views.PublicationViewSet)
storyRoutes = router.register('stories', views.StoryViewSet)
storyRoutes.register(
    'comments', 
    views.CommentViewSet, 
    base_name="story-comments", 
    parents_query_lookups=['story']
)
router.register('categories', views.CategoryViewSet)
router.register('comments', views.CommentViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^users/?$', Signup.as_view(), name="signup"),
    url(r'^users/analytics/?$', UpdateAnalytics.as_view(), name="update_analytics"),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
]
