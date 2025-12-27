from rest_framework import serializers
from . import models
from accounts_app.models import User


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        fields = [
            "id",
            "name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    org = serializers.PrimaryKeyRelatedField(queryset=models.Organization.objects.all())

    class Meta:
        model = models.OrganizationMember
        fields = [
            "id",
            "org",
            "user",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
