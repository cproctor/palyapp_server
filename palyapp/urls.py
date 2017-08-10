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
from profiles.views import Signup, UpdateAnalytics, UpdateDeviceToken

# ===================================== V1 API =====================================
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

# Workaround to support slashes or not in URLs.
slashless_router = routers.ExtendedDefaultRouter(trailing_slash=False)
slashless_router.register('publications', views.PublicationViewSet)
storyRoutes = slashless_router.register('stories', views.StoryViewSet)
storyRoutes.register(
    'comments',
    views.CommentViewSet,
    base_name="story-comments",
    parents_query_lookups=['story']
)
slashless_router.register('categories', views.CategoryViewSet)
slashless_router.register('comments', views.CommentViewSet)

# ===================================== V2 API =====================================
from stories2 import views as views2
from profiles2.views import ProfileViewSet

router2 = routers.ExtendedDefaultRouter()
slashless_router2 = routers.ExtendedDefaultRouter(trailing_slash=False)
flagrouter = routers.SimpleRouter()

for r in (router2, slashless_router2):
    r.register('users', ProfileViewSet, base_name='user')
    r.register('feed', views2.FeedViewSet)
    r.register('publications', views2.PublicationViewSet)
    r.register('comments', views2.CommentViewSet)
    storyRoutes = r.register('stories', views2.StoryViewSet)
    storyRoutes.register(
        'comments',
        views2.CommentViewSet,
        base_name="story-comments",
        parents_query_lookups=['story']
    )
    topicRoutes = r.register('topics', views2.TopicViewSet)
    topicRoutes.register(
        'comments',
        views2.CommentViewSet,
        base_name="topic-comments",
        parents_query_lookups=['topic']
    )

flagrouter.register(r'flagged_comments', views2.FlaggedViewSet)

# ===================================== Global =====================================
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(slashless_router.urls)),
    url(r'^users/?$', Signup.as_view(), name="signup"),
    url(r'^users/analytics/?$', UpdateAnalytics.as_view(), name="update_analytics"),
    url(r'^users/devicetoken/?$', UpdateDeviceToken.as_view(), name="update_device_token"),

    url(r'^v2/', include(router2.urls, namespace='v2')),
    url(r'^v2/', include(slashless_router2.urls, namespace='v2_no_slash')),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
    
    url(r'^v2/admin/', include(flagrouter.urls)),
]
