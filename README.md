# Looply — Django Social Media App

A responsive Django social-media project with account registration/login, profiles, image/text posts, likes, comments, user search/discovery, follow/unfollow, and in-app notifications.

## Requirements
- Python 3.10+
- Django 5.2 or 6.0
- Pillow (for image upload support)

## Setup (Windows)
Open a terminal in the folder containing `manage.py` and run:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py runserver
```

Then open http://127.0.0.1:8000/ . The root URL shows the welcome page for logged-out visitors and redirects signed-in users to the feed.

## Useful URLs
- `/` — welcome page / root route
- `/accounts/register/` — create account
- `/accounts/login/` — log in
- `/posts/` — feed (login required)
- `/accounts/discover/` — discover and follow users
- `/core/search/` — search people and posts
- `/core/notifications/` — notifications
- `/admin/` — Django admin

## Notes
- SQLite is configured by default.
- For a fresh installation, `python manage.py migrate` creates the database tables.
- Before production deployment, set `DEBUG = False`, configure `ALLOWED_HOSTS`, use a private `SECRET_KEY`, and configure static/media hosting.
