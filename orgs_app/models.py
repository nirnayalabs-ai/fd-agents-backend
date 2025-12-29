from django.db import models
from helper.models import UUIDPrimaryKey, IsActiveModel, TimeLine
from accounts_app.models import User
from .managers import OrganizationScopedManager

class Organization(UUIDPrimaryKey, IsActiveModel, TimeLine):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class OrganizationFieldMixin(models.Model):
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )

    objects : OrganizationScopedManager = OrganizationScopedManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True


class OrganizationMember(UUIDPrimaryKey, IsActiveModel, TimeLine, OrganizationFieldMixin):
    class Roles(models.TextChoices):
        ORG_OWNER = "org_owner", "Organization Owner"
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        MEMBER = "member", "Member"
        VIEWER = "viewer", "Viewer"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organization_memberships"
    )

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.MEMBER
    )

    class Meta:
        unique_together = ("org", "user")

    def __str__(self):
        return f"{self.user.email} → {self.org.name} ({self.role})"


class LLMProvider(UUIDPrimaryKey, IsActiveModel, TimeLine):
    name = models.CharField(max_length=150, unique=True)


class LLMModel(UUIDPrimaryKey, IsActiveModel, TimeLine):
    provider = models.ForeignKey(LLMProvider, on_delete=models.CASCADE)
    model_key = models.CharField(max_length=100)
    display_name = models.CharField(max_length=150)
    context_length = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("provider", "model_key")


class OrganizationLLMConfig(UUIDPrimaryKey, IsActiveModel, TimeLine, OrganizationFieldMixin):
    provider = models.ForeignKey(LLMProvider, on_delete=models.CASCADE, related_name="orgs")
    api_key = models.TextField()
