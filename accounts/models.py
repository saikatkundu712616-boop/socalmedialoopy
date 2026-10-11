from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Profile(models.Model):
    """
    One-to-One extension of Django's built-in User model.
    Holds social-media-specific fields (bio, avatar, website, location).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(max_length=300, blank=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default_avatar.png',
        blank=True
    )
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def followers_count(self):
        return self.user.followers.count()

    @property
    def following_count(self):
        return self.user.following.count()




class Follow(models.Model):
    """
    Self-referential M2M through table for the follow system.
    follower -> the user who clicks 'Follow'
    following -> the user being followed
    """
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='following',      # user.following.all() -> who I follow
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='followers',      # user.followers.all() -> who follows me
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_profile(sender, instance, created, **kwargs):
    """
    Auto-create a Profile whenever a new User is created.
    Keeps things clean — no manual Profile creation needed in views.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        # In case profile was deleted somehow, re-create on save
        Profile.objects.get_or_create(user=instance)