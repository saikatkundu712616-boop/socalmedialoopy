# core/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


# ---------------------------------------------------------------------
# 1. Site Settings — singleton row for global UI content
# ---------------------------------------------------------------------
class SiteSettings(models.Model):
    """
    A single-row table to store site-wide content that an admin
    can edit from Django admin (site name, tagline, banner, footer).
    Use: SiteSettings.load()
    """
    site_name = models.CharField(max_length=80, default='Looply')
    tagline = models.CharField(max_length=160, blank=True)
    about_text = models.TextField(blank=True)
    banner_image = models.ImageField(
        upload_to='site/',
        blank=True,
        null=True
    )
    contact_email = models.EmailField(blank=True)
    maintenance_mode = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Enforce singleton: always id=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ---------------------------------------------------------------------
# 2. Notification — cross-cutting concern for the whole platform
# ---------------------------------------------------------------------
class Notification(models.Model):
    """
    Generic notification row, created when a user is followed,
    a post is liked, or a comment is added.

    Use Notification.objects.create(
        recipient=some_user,
        actor=request.user,
        verb='liked your post',
        target_url=f'/posts/{post.id}/'
    )
    """

    class Verb(models.TextChoices):
        FOLLOWED = 'followed', 'Started following you'
        LIKED = 'liked', 'Liked your post'
        COMMENTED = 'commented', 'Commented on your post'
        MENTIONED = 'mentioned', 'Mentioned you'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        on_delete=models.CASCADE
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='actions',
        on_delete=models.CASCADE
    )
    verb = models.CharField(max_length=20, choices=Verb.choices)
    target_url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"[{self.verb}] {self.actor.username} → {self.recipient.username}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])


# ---------------------------------------------------------------------
# 3. Contact / Feedback message (optional but nice for a portfolio app)
# ---------------------------------------------------------------------
class ContactMessage(models.Model):
    """
    Simple contact form submissions from the landing page.
    """
    name = models.CharField(max_length=80)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.subject}"