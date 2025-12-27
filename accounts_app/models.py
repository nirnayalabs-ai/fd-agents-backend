from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from helper.models import UUIDPrimaryKey, IsActiveModel, TimeLine
from django.utils.timezone import now, timedelta
from django.core.validators import RegexValidator
from helper.mails import send_invitation_email
    
from .managers import UserManager


class User(UUIDPrimaryKey, IsActiveModel, AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    date_joined = models.DateTimeField(auto_now_add=True)

    objects : UserManager = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Invitation(UUIDPrimaryKey, TimeLine):
    from_email = models.EmailField(
        null=True,
        validators=[
            RegexValidator(
                regex=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
                message="Enter a valid email address."
            )
        ]
    )
    to_email = models.EmailField(
        
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
                message="Enter a valid email address."
            )
        ]
    )
    
    token = models.TextField(unique=True)
    is_accepted = models.BooleanField(default=False)
    
    @property    
    def is_expired(self):
        return self.is_accepted or self.created_at < now() - timedelta(days=1)        
    
    def send_invitation_email(self):
        return send_invitation_email(self)
    

    def __str__(self):
        return f"To - {self.to_email}"
