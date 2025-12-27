from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from orgs_app.models import OrganizationMember
from config import context_storage


def get_org():
    return context_storage.get_current_org()


def get_org_member(user, organization):
    try:
        return OrganizationMember.objects.get(user=user, org=organization)
    except OrganizationMember.DoesNotExist:
        return None


class BaseOrgRolePermission(BasePermission):
    """
    Base permission that checks if the user has one of the allowed roles.
    """

    allowed_roles = []

    def has_permission(self, request, view):
        org = get_org()
        if not org:
            return False

        member = get_org_member(request.user, org)
        if not member:
            return False

        return member.role in self.allowed_roles


class IsOrgOwner(BaseOrgRolePermission):
    allowed_roles = [OrganizationMember.Roles.ORG_OWNER]


class IsOrgAdmin(BaseOrgRolePermission):
    allowed_roles = [
        OrganizationMember.Roles.ORG_OWNER,
        OrganizationMember.Roles.ADMIN,
    ]


class IsOrgManager(BaseOrgRolePermission):
    allowed_roles = [
        OrganizationMember.Roles.ORG_OWNER,
        OrganizationMember.Roles.ADMIN,
        OrganizationMember.Roles.MANAGER,
    ]


class IsOrgMember(BaseOrgRolePermission):
    allowed_roles = [
        OrganizationMember.Roles.ORG_OWNER,
        OrganizationMember.Roles.ADMIN,
        OrganizationMember.Roles.MANAGER,
        OrganizationMember.Roles.MEMBER,
    ]


class IsOrgViewerOrAbove(BaseOrgRolePermission):
    allowed_roles = [
        OrganizationMember.Roles.ORG_OWNER,
        OrganizationMember.Roles.ADMIN,
        OrganizationMember.Roles.MANAGER,
        OrganizationMember.Roles.MEMBER,
        OrganizationMember.Roles.VIEWER,
    ]


class CanManageRoles(BasePermission):
    """
    Allows a user to manage other members only if the target's role
    is lower in hierarchy than the current user's role.
    """

    ROLE_HIERARCHY = {
        OrganizationMember.Roles.ORG_OWNER: 5,
        OrganizationMember.Roles.ADMIN: 4,
        OrganizationMember.Roles.MANAGER: 3,
        OrganizationMember.Roles.MEMBER: 2,
        OrganizationMember.Roles.VIEWER: 1,
    }

    def has_permission(self, request, view):
        # Only allow authenticated users
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        obj is the OrganizationMember instance being managed
        """
        current_org = get_org()
        if not current_org:
            return False

        try:
            current_member = OrganizationMember.objects.get(
                user=request.user,
                org=current_org
            )
        except OrganizationMember.DoesNotExist:
            return False

        # Current user's role power
        current_role_power = self.ROLE_HIERARCHY.get(current_member.role, 0)
        # Target user's role power
        target_role_power = self.ROLE_HIERARCHY.get(obj.role, 0)

        # Can manage only if target's role is lower
        return current_role_power > target_role_power


class ReadOnly(IsAuthenticated):
    """
    Read (GET, HEAD, OPTIONS) → IsOrgViewer
    """

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if request.method in SAFE_METHODS:
                return IsOrgViewerOrAbove().has_permission(request, view)
            return False
        return False