from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models
from orgs_app.models import Organization, OrganizationMember


@receiver(post_save, sender=models.Invitation)
def send_invitation_email(sender, instance: models.Invitation, created, **kwargs):
    """
    Sends an invitation email to the recipient when an invitation is created.
    """
    if created:
        instance.send_invitation_email()


@receiver(post_save, sender=models.User)
def setup_user_organization(sender, instance: models.User, created, **kwargs):
    """
    Sends an invitation email to the recipient when an invitation is created.
    """
    if created:
        org_name = instance.last_name
        user_org = Organization.objects.create(name = org_name)
        OrganizationMember.objects.create(
            org = user_org,
            user = instance,
            role = OrganizationMember.Roles.ORG_OWNER
        )
