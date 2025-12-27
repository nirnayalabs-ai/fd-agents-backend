from django.http import JsonResponse
from config import context_storage
from orgs_app.models import Organization


class OrganizationAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def authenticate_organization(self, org_id):
        return Organization.objects.filter(id=org_id).first()

    def __call__(self, request):
        org_id = request.headers.get("X-Org-ID")

        if org_id:
            context_storage.clear()
            org_id = str(org_id).strip()

            org = self.authenticate_organization(org_id)

            if not org:
                context_storage.clear()
                return JsonResponse(
                    {"detail": "Invalid organization or organization not found"},
                    status=403
                )

            context_storage.set_current_org(org)

        response = self.get_response(request)

        if not getattr(response, "streaming", False):
            context_storage.clear()

        return response
