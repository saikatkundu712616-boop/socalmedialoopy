from django.contrib import admin
from accounts.models import Profile, Follow

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'website', 'created_at')
    search_fields = ('user__username', 'user__email')

@admin.register(Follow)
class FollwAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')