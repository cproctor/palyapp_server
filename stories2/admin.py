from stories2.models import Publication, Category, Story, Topic, Comment
from django.contrib import admin

# Register your models here.

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    pass

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
