from django.contrib import admin

from posts.models import Post, Comment, Like
# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'short_content', 'created_at', 'likes_count')
    search_fields = ('author__username', 'content')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

    def short_content(self, obj):
        return obj.content[:50]
    short_content.short_description = 'Content'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'short_content', 'created_at')
    search_fields = ('author__username', 'content')
    ordering = ('-created_at',)

    def short_content(self, obj):
        return obj.content[:50]
    short_content.short_description = 'Comment'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'created_at')
    search_fields = ('user__username',)
    ordering = ('-created_at',)