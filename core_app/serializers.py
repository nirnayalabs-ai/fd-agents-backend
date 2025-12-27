from rest_framework import serializers
from .models import Project, Agent, Debate, DebateMessage, LLMModelLog
from orgs_app.models import Organization
from config import context_storage

class OrganizationSerializerMixin(serializers.Serializer):
    """
    Mixin to handle organization assignment.

    Behavior:
    - If `org` is provided in request data → use it
    - If not provided → fallback to context_storage.get_current_org()
    """

    org = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        allow_null=True
    )

    def validate(self, attrs):
        if attrs.get("org"):
            return attrs

        org = context_storage.get_current_org()
        if not org:
            raise serializers.ValidationError(
                {"org": "Organization could not be resolved."}
            )
        attrs["org"] = org
        return attrs
    

class ProjectSerializer(serializers.ModelSerializer, OrganizationSerializerMixin):
    
    class Meta:
        model = Project
        fields = "__all__"


class AgentSerializer(serializers.ModelSerializer, OrganizationSerializerMixin):
    
    class Meta:
        model = Agent
        fields = "__all__"


class DebateSerializer(serializers.ModelSerializer, OrganizationSerializerMixin):
    agents = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Agent.objects.all()
    )

    class Meta:
        model = Debate
        fields = "__all__"


class DebateMessageSerializer(serializers.ModelSerializer, OrganizationSerializerMixin):
    
    class Meta:
        model = DebateMessage
        fields = "__all__"


class LLMModelLogSerializer(serializers.ModelSerializer, OrganizationSerializerMixin):

    class Meta:
        model = LLMModelLog
        fields = "__all__"
