from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def get_or_create_user(self, email, first_name=None, last_name=None, password=None, **extra_fields):
        """
        Returns existing user or creates a new one.
        Same behavior as Django's get_or_create, but allows password setting.
        """
        email = self.normalize_email(email)

        try:
            user = self.get(email=email)
            return user, False   # False → Not created

        except self.model.DoesNotExist:
            # Create new user
            user = self.create_user(
                email=email,
                first_name=first_name or "",
                last_name=last_name or "",
                password=password,
                **extra_fields
            )
            return user, True