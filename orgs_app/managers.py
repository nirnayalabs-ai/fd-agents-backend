from django.db import models
from config import context_storage

class OrganizationScopedQuerySet(models.QuerySet):
    def for_current_org(self):
        current_org = context_storage.get_current_org()
        if not current_org:
            return self.none()
        return self.filter(org=current_org)
    
    def all(self):
        return self.for_current_org()


class OrganizationScopedManager(models.Manager):
    def get_queryset(self):
        return OrganizationScopedQuerySet(self.model, using=self._db).for_current_org()


