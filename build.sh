#!/usr/bin/env bash

pip install -r requirements.txt

python manage.py migrate

python manage.py collectstatic --noinput

# Create users (admin + roles)
echo "
from django.contrib.auth import get_user_model
User = get_user_model()

# ---------------- ADMIN ----------------
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@gmail.com', 'admin123')

# ---------------- ROLE USERS ----------------
users = [
    ('cc_user', 'Pass@123'),
    ('hod_user', 'CSEHod@124'),
    ('rector_user', 'Rector@124'),
]

for username, password in users:
    if not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username=username, password=password)
        u.is_staff = True
        u.save()
" | python manage.py shell