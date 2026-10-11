# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q

from core.models import Notification, SiteSettings, ContactMessage
from posts.models import Post, Like
from accounts.models import Follow


def home_view(request):
    """
    Landing page for anonymous users.
    Logged-in users get redirected straight to the feed.
    """
    if request.user.is_authenticated:
        return redirect('posts:feed')
    return render(request, 'core/home.html', {
        'settings': SiteSettings.load(),
    })


@login_required
def notifications_view(request):
    """List all notifications for the current user."""
    notifications = (
        Notification.objects
        .filter(recipient=request.user)
        .select_related('actor', 'actor__profile')
    )

    # Mark them all as read when the user opens the page
    Notification.objects.filter(
        recipient=request.user, is_read=False
    ).update(is_read=True)

    return render(request, 'core/notification.html', {
        'notifications': notifications,
    })


@login_required
def search_view(request):
    """
    Simple search across users and post content.
    GET /search/?q=hello
    """
    from posts.models import Post, Like   # local import to avoid any circular-import risk

    q = request.GET.get('q', '').strip()
    users = []
    posts = []
    liked_post_ids = set()

    if q:
        # --- Search users ---
        users = (
            request.user.__class__.objects
            .filter(
                Q(username__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)
            )
            .exclude(pk=request.user.pk)
            .select_related('profile')[:20]
        )

        # --- Search posts ---
        posts = (
            Post.objects
            .filter(content__icontains=q)
            .select_related('author', 'author__profile')
            .prefetch_related('likes', 'comments')
            .order_by('-created_at')[:30]
        )

        # --- Which of these posts has the current user liked? ---
        liked_post_ids = set(
            Like.objects
            .filter(user=request.user, post__in=posts)
            .values_list('post_id', flat=True)
        )

    return render(request, 'core/search_results.html', {
        'q': q,
        'users': users,
        'posts': posts,
        'liked_post_ids': liked_post_ids,   # <-- required by post_card.html
    })


def contact_view(request):
    """Optional contact form — saves to ContactMessage."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_body = request.POST.get('message', '').strip()

        if not all([name, email, subject, message_body]):
            messages.error(request, "All fields are required.")
        else:
            ContactMessage.objects.create(
                name=name, email=email,
                subject=subject, message=message_body
            )
            messages.success(request, "Message sent. We'll get back to you soon.")
            return redirect('core:contact')

    return render(request, 'core/contact.html')


@login_required
def unread_notifications_count(request):
    """
    Optional JSON endpoint — the navbar JS can call this
    to show a badge count without loading the full page.
    """
    from django.http import JsonResponse
    count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()
    return JsonResponse({'count': count})