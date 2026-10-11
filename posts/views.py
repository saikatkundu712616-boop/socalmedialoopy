# posts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q

from accounts.models import Follow
from posts.models import Post, Comment, Like


# ------------------------------------------------------------------
# Helper
# ------------------------------------------------------------------
def _liked_ids(user, posts):
    """Return a set of post IDs the given user has liked (from a queryset)."""
    if not user.is_authenticated:
        return set()
    return set(
        Like.objects.filter(user=user, post__in=posts)
        .values_list('post_id', flat=True)
    )


# ------------------------------------------------------------------
# FEED
# ------------------------------------------------------------------
@login_required
def feed_view(request):
    """
    Show posts from users the request.user follows + their own posts.
    If the user follows nobody, show their own posts only.
    """
    following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list('following_id', flat=True)

    posts = (
        Post.objects
        .filter(Q(author__in=following_ids) | Q(author=request.user))
        .select_related('author', 'author__profile')
        .prefetch_related('likes', 'comments', 'comments__author')
    )

    liked_post_ids = set(
    Like.objects.filter(user=request.user, post__in=posts)
    .values_list('post_id', flat=True)
)

    return render(request, 'posts/feed.html', {
        'posts': posts,
        'liked_post_ids': liked_post_ids,
    })


# ------------------------------------------------------------------
# CREATE / EDIT / DELETE
# ------------------------------------------------------------------
@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')

        if not content and not image:
            messages.error(request, "Post cannot be empty.")
            return redirect('posts:create_post')

        Post.objects.create(
            author=request.user, content=content, image=image
        )
        messages.success(request, "Post created.")
        return redirect('posts:feed')

    return render(request, 'posts/create_post.html')


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        messages.error(request, "You can only edit your own posts.")
        return redirect('posts:feed')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')
        remove_image = request.POST.get('remove_image') == 'on'

        if not content and not image and not post.image:
            messages.error(request, "Post cannot be empty.")
            return render(request, 'posts/edit_post.html', {'post': post})

        post.content = content
        if image:
            post.image = image
        elif remove_image:
            post.image = None

        post.save()
        messages.success(request, "Post updated.")
        return redirect('posts:post_detail', pk=post.pk)

    return render(request, 'posts/edit_post.html', {'post': post})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "You can only delete your own posts.")
        return redirect('posts:feed')

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect('posts:feed')

    return render(request, 'posts/post_detail.html', {
        'post': post, 'confirm_delete': True,
    })


# ------------------------------------------------------------------
# DETAIL
# ------------------------------------------------------------------
@login_required
def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__profile')
                    .prefetch_related('comments__author', 'likes'),
        pk=pk
    )
    liked = Like.objects.filter(post=post, user=request.user).exists()
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'liked': liked,
    })


# ------------------------------------------------------------------
# LIKE (AJAX)
# ------------------------------------------------------------------
@require_POST
@login_required
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)

    like, created = Like.objects.get_or_create(post=post, user=request.user)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        # Create notification (skip if liking your own post)
        if post.author != request.user:
            try:
                from core.models import Notification
                Notification.objects.create(
                    recipient=post.author,
                    actor=request.user,
                    verb=Notification.Verb.LIKED,
                    target_url=f'/posts/{post.pk}/',
                )
            except Exception:
                pass

    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count(),
    })


# ------------------------------------------------------------------
# COMMENTS (AJAX)
# ------------------------------------------------------------------
@require_POST
@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'error': 'Comment cannot be empty.'}, status=400)

    comment = Comment.objects.create(
        post=post, author=request.user, content=content
    )

    # Notification
    if post.author != request.user:
        try:
            from core.models import Notification
            Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                verb=Notification.Verb.COMMENTED,
                target_url=f'/posts/{post.pk}/',
            )
        except Exception:
            pass

    return JsonResponse({
        'id': comment.id,
        'author': comment.author.username,
        'author_avatar': comment.author.profile.avatar.url,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%b %d, %Y %H:%M'),
        'comments_count': post.comments.count(),
    })


@require_POST
@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post

    if comment.author != request.user and post.author != request.user:
        return JsonResponse({'error': 'Not allowed.'}, status=403)

    comment.delete()
    return JsonResponse({
        'deleted': True,
        'comments_count': post.comments.count(),
    })