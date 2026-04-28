#!/usr/bin/env bash

pip install -r requirements.txt

python manage.py migrate

python manage.py collectstatic --noinput

# Create superuser automatically
echo "from django.contrib.auth.models import User;
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin','admin@gmail.com','admin123')" | python manage.py shell