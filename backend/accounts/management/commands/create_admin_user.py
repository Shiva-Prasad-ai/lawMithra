"""
Django management command to create or update an administrator account safely.
Idempotent and safe to run multiple times.
Usage: python manage.py create_admin_user
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = "Creates or updates a development administrator (superuser) account for Law Mithra"

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default=os.environ.get('ADMIN_EMAIL', 'admin@lawmithra.in'),
            help='Admin email address / username'
        )
        parser.add_argument(
            '--password',
            type=str,
            default=os.environ.get('ADMIN_PASSWORD', 'LawMithra@Admin2026!'),
            help='Admin password'
        )

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        password = options['password']

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': 'System Administrator',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )

        user.username = email
        user.first_name = 'System Administrator'
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'preferred_language': UserProfile.Language.ENGLISH,
                'text_size': UserProfile.TextSize.NORMAL,
            }
        )

        action = "Created new" if created else "Updated existing"
        self.stdout.write(self.style.SUCCESS(f"[Law Mithra] {action} admin account:"))
        self.stdout.write(f"  Email: {email}")
        self.stdout.write(f"  Role: Superuser / Staff Administrator")
        self.stdout.write(f"  Status: Active")

