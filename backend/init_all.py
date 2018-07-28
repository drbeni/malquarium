#!/usr/bin/env python3

import os
import subprocess
import time

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "malquarium.settings")
django.setup()


def init_all_the_things():
    # sleep some seconds to give postgresql time to startup and initialize
    time.sleep(15)

    initialize_database()
    create_superuser()


def create_superuser():
    User.objects.create_superuser(
        os.getenv('ADMIN_USER', 'admin'),
        os.getenv('ADMIN_EMAIL', 'admin@example.com'),
        os.getenv('ADMIN_PASSWORD', 'changeme')
    )


def initialize_database():
    subprocess.check_call(["/app/env/malquarium/bin/python3", "/app/manage.py", "makemigrations", "backend"])

    subprocess.check_call(["/app/env/malquarium/bin/python3", "/app/manage.py", "migrate", "--noinput"])
    subprocess.check_call(
        ["/app/env/malquarium/bin/python3", "/app/manage.py", "loaddata", "backend/fixtures/profile_fixtures.json"])
    subprocess.check_call([
        "/app/env/malquarium/bin/python3", "/app/manage.py", "loaddata", "backend/fixtures/analyzer_fixtures.json"])


if __name__ == '__main__':
    from django.contrib.auth.models import User

    try:
        User.objects.count()
        exit(0)
    except Exception as e:
        print(e)
        init_all_the_things()
