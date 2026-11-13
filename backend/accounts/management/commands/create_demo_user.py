"""
Django management command to create or update the demo account safely.
Idempotent and safe to run multiple times.
Usage: python manage.py create_demo_user
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = "Creates or updates the demonstration account for Law Mithra"

    def handle(self, *args, **options):
        email = os.environ.get("DEMO_USER_EMAIL", "lawmithra@gmail.com").strip().lower()
        password = os.environ.get("DEMO_USER_PASSWORD", "lawmithra2026")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "is_active": True,
            }
        )

        user.username = email
        user.is_active = True
        user.set_password(password)
        user.save()

        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "preferred_language": UserProfile.Language.ENGLISH,
                "text_size": UserProfile.TextSize.NORMAL,
            }
        )

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} demo user: {email}"))

