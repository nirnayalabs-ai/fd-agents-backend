from django.db import transaction
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from accounts_app.models import User
from django.core.validators import validate_email
from getpass import getpass


class Command(BaseCommand):
    help = "Create a normal user interactively"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Creating a new user"))

        # Ask for email
        while True:
            email = input("Email: ").strip()
            try:
                validate_email(email)
                if User.objects.filter(email=email).exists():
                    self.stdout.write(self.style.ERROR("Email already exists!"))
                    continue
                break
            except ValidationError:
                self.stdout.write(self.style.ERROR("Invalid email. Please try again."))

        # Ask for first name
        first_name = input("First name: ").strip()

        # Ask for last name
        last_name = input("Last name: ").strip()

        # Ask for password
        while True:
            password = getpass("Password: ")
            password2 = getpass("Password (again): ")
            if password != password2:
                self.stdout.write(self.style.ERROR("Passwords do not match. Try again."))
            else:
                break

        # Create user
        with transaction.atomic():
            user : User = User.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )

        self.stdout.write(self.style.SUCCESS(f"User created successfully: {user.email}"))
