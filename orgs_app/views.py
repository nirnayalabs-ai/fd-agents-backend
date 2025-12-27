from rest_framework import viewsets, response
from helper.exceptions import SmoothException
from . import models, permissions
from .serializers import OrganizationSerializer, OrganizationMemberSerializer
from config import context_storage


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = models.Organization.objects.all()
    serializer_class = OrganizationSerializer


    def create(self, request, *args, **kwargs):
        raise SmoothException.warning(
            detail="Creation of organizations is not allowed.",
            dev_message="POST /organizations/ is blocked by system restriction."
        )


class OrganizationMemberViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationMemberSerializer
    permission_classes = [permissions.CanManageRoles]

    def get_queryset(self):
        current_org = context_storage.get_current_org()
        if not current_org:
            return models.OrganizationMember.objects.none()

        # Get current user's role
        try:
            current_member = models.OrganizationMember.objects.get(
                user=self.request.user,
                org=current_org
            )
        except models.OrganizationMember.DoesNotExist:
            return models.OrganizationMember.objects.none()

        ROLE_HIERARCHY = {
            "org_owner": 5,
            "admin": 4,
            "manager": 3,
            "member": 2,
            "viewer": 1
        }

        current_power = ROLE_HIERARCHY.get(current_member.role, 0)

        # Return only members with role lower than or equal to current user's role
        # If you want members to see only same level or below
        return models.OrganizationMember.objects.filter(
            org=current_org,
            role__in=[
                role for role, power in ROLE_HIERARCHY.items()
                if power <= current_power
            ]
        ).select_related("user", "org")