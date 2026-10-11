from django.db import models
from django.conf import settings
from django.urls import reverse

# Create your models here.

class Post(models.Model):
    #  A single text/image post created by a user

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='posts',
        on_delete=models.CASCADE
    )
    content = models.TextField(max_length=1000, blank=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:40]}"

    def get_absolute_url(self):
        return reverse("posts:post_detail", args=[self.pk])

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()



class Comment(models.Model):
    # comment on a post


    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE
    )    

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments',
        on_delete=models.CASCADE
    )

    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username} on post #{self.post.id}"



class Like(models.Model):


    """
    A like on a Post by a User.
    unique_together prevents double-likes.
    """
    post = models.ForeignKey(
            Post,
            related_name='likes',
            on_delete=models.CASCADE
        )    
    
    user = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name='likes',
            on_delete=models.CASCADE
        )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ♥ post #{self.post.id}"