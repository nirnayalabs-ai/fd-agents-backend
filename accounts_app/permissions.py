import os
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from core_app import models
from helper import exceptions

class AppPermission(BasePermission):
    """
    Custom permission class for managing access to specific app-related views.
    """
        
    def has_permission(self, request, view):
        return True
        """
        Check if the user has permission to access the app-related views.   
        """
        app_slug = app_slug = os.environ.get('GLOBAL_FEATURE_SLUG', None) or getattr(view, 'app_slug', None)
        if app_slug is None:
            raise exceptions.SmoothException.error(
                detail="App Slug was not found in the App permission class / View",
                dev_message="Ensure that the App Slug is correctly passed in the request and is handled in the permission class."
            )


        user_permissions : models.UserPermissions = models.UserPermissions.objects.get(user=request.user)
        user_permissions.sync_permissions()
        permissions = user_permissions.permissions        
        if permissions.get(app_slug, False):
            return True
        raise PermissionDenied(f"You don't have {app_slug.replace('_', ' ').title()} feature access/permission")

            
