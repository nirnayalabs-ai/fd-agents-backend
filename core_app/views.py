from django.http import StreamingHttpResponse
from rest_framework import viewsets, generics
from orgs_app import permissions
from .models import Project, Agent, Debate, DebateMessage
from .serializers import (
    ProjectSerializer,
    AgentSerializer,
    DebateSerializer,
    DebateMessageSerializer
)
from config import context_storage

from .processors import DebateCreateProcessor, DebateFlowProcessor

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsOrgMember]

    def get_queryset(self):
        """
        This method is called for every request.
        By this time, your middleware has run and context_storage 
        has the organization data.
        """
        return Project.objects.all()


class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AgentSerializer
    permission_classes = [permissions.IsOrgMember]

    def get_queryset(self):
        """
        This method is called for every request.
        By this time, your middleware has run and context_storage 
        has the organization data.
        """
        return Agent.objects.all()

class DebateViewSet(viewsets.ModelViewSet):
    serializer_class = DebateSerializer
    permission_classes = [permissions.IsOrgMember]

    def get_queryset(self):
        """
        This method is called for every request.
        By this time, your middleware has run and context_storage 
        has the organization data.
        """
        return Debate.objects.all()

    def create(self, request, *args, **kwargs):
        debate_processor = DebateCreateProcessor(request, project_id=request.data.get("project"))
        return StreamingHttpResponse(debate_processor.process(), content_type='text/event-stream')


class DebateMessageViewSet(viewsets.ModelViewSet):
    serializer_class = DebateMessageSerializer
    permission_classes = [permissions.IsOrgMember]

    def get_queryset(self):
        """
        This method is called for every request.
        By this time, your middleware has run and context_storage 
        has the organization data.
        """
        return DebateMessage.objects.all()

class StartOrContinueDebateView(generics.UpdateAPIView):
    serializer_class = DebateSerializer
    permission_classes = [permissions.IsOrgMember]

    def get_queryset(self):
        """
        This method is called for every request.
        By this time, your middleware has run and context_storage 
        has the organization data.
        """
        return Debate.objects.all()

    def update(self, request, *args, **kwargs):
        debate = self.get_object()
        debate_processor = DebateFlowProcessor(request, debate=debate)
        return StreamingHttpResponse(debate_processor.process(), content_type='text/event-stream')
