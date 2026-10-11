from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (
    authenticate, login, logout, get_user_model
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils.http import url_has_allowed_host_and_scheme

from accounts.models import Profile, Follow
from posts.models import Post, Like


# Create your views here.

User = get_user_model()



#           AUTHENTICATIION

def register_view(request):
    """Register a new user via raw POST. No forms.py."""
    if request.user.is_authenticated:
        return redirect('posts:feed')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')

        # ---- validation ----
        errors = []
        if not username or not email or not password:
            errors.append("All fields are required.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if User.objects.filter(username__iexact=username).exists():
            errors.append("Username is already taken.")
        if User.objects.filter(email__iexact=email).exists():
            errors.append("Email is already registered.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'accounts/register.html', {
                'username': username,
                'email': email,
            })

        # ---- create user ----
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        login(request, user)
        messages.success(request, f"Welcome, {user.username}!")
        return redirect('posts:feed')

    # ---- GET request: show the form ----
    return render(request, 'accounts/register.html')


#           LOGIN VIEW
def login_view(request):
    if request.user.is_authenticated:
        return redirect('posts:feed')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next') or request.GET.get('next')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(next_url)
            return redirect('posts:feed')
        messages.error(request, "Invalid username or password.")
        return render(request, 'accounts/login.html', {'username': username})

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have bee logged out.")
    return redirect('accounts:login')



# -----------------PROFILE---------------

@login_required
def profile_view(request, username):
    from posts.models import Like   # local import to avoid circular import

    profile_user = get_object_or_404(User, username=username)
    Profile.objects.get_or_create(user=profile_user)

    posts = (
        profile_user.posts
        .select_related('author', 'author__profile')
        .prefetch_related('likes', 'comments', 'comments__author')
        .order_by('-created_at')
    )

    liked_post_ids = set(
        Like.objects
        .filter(user=request.user, post__in=posts)
        .values_list('post_id', flat=True)
    )

    is_following = Follow.objects.filter(
        follower=request.user, following=profile_user
    ).exists()

    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'followers_count': profile_user.followers.count(),
        'following_count': profile_user.following.count(),
        'is_own_profile': request.user == profile_user,
        'liked_post_ids': liked_post_ids,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update User fields
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()

        if username and username != request.user.username:
            if User.objects.filter(username__iexact=username).exclude(pk=request.user.pk).exists():
                messages.error(request, "That username is taken.")
                return redirect('accounts:edit_profile')
            request.user.username = username

        if email and email != request.user.email:
            if User.objects.filter(email__iexact=email).exclude(pk=request.user.pk).exists():
                messages.error(request, "That email is in use.")
                return redirect('accounts:edit_profile')
            request.user.email = email

        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.save()

        # Update Profile fields
        profile.bio = request.POST.get('bio', '').strip()
        profile.website = request.POST.get('website', '').strip()
        profile.location = request.POST.get('location', '').strip()

        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']

        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('accounts:profile', username=request.user.username)
    
    return render(request, 'accounts/edit_profile.html', {
        'profile': profile,
    })



    # FOLLOW SYSTEM (AJAX)

@require_POST
@login_required
def follow_toggle(request, username):
    target = get_object_or_404(User, username=username)

    if target == request.user:
        return JsonResponse(
            {'error': 'You cannot follow yourself.'}, status=400
        )

    obj, created = Follow.objects.get_or_create(
        follower=request.user, following=target
    )

    if not created:
        obj.delete()
        following = False
    else:
        following = True
        # Optional notification
        try:
            from core.models import Notification
            if hasattr(Notification, 'Verb'):
                Notification.objects.create(
                    recipient=target,
                    actor=request.user,
                    verb=Notification.Verb.FOLLOWED,
                    target_url=f'/accounts/profile/{request.user.username}/',
                )
        except Exception:
            pass

    return JsonResponse({
        'following': following,
        'followers_count': target.followers.count(),
        'following_count': request.user.following.count(),
    })


                # LISTS

@login_required
def followers_list(request, username):
    user_obj = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=user_obj).select_related('follower')
    return render(request, 'accounts/followers_list.html', {
        'user_obj': user_obj,
        'items': [f.follower for f in followers],
        'title': f"Followers of {user_obj.username}",
        'empty_msg': "No followers yet.",
    })


@login_required
def following_list(request, username):
    user_obj = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=user_obj).select_related('following')
    return render(request, 'accounts/followers_list.html', {
        'user_obj': user_obj,
        'items': [f.following for f in following],
        'title': f"{user_obj.username} follows",
        'empty_msg': "Not following anyone yet.",
    })



@login_required
def discover_view(request):
    """
    Show all users except the logged-in user, with a follow/unfollow button.
    """
    # Get all users except yourself, optimized with select_related
    users = (
        User.objects
        .exclude(pk=request.user.pk)
        .select_related('profile')
        .order_by('-date_joined')
    )

    # Build a set of user IDs that the current user is following
    following_ids = set(
        Follow.objects
        .filter(follower=request.user)
        .values_list('following_id', flat=True)
    )

    return render(request, 'accounts/discover.html', {
        'users': users,
        'following_ids': following_ids,
        'users_count': users.count(),
    })