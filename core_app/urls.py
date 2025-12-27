from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    AgentViewSet,
    DebateViewSet,
    DebateMessageViewSet,
    StartOrContinueDebateView,
)

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")
router.register("agents", AgentViewSet, basename="agent")
router.register("debates", DebateViewSet, basename="debate")
router.register("agents_messages", DebateMessageViewSet, basename="debate_message")

urlpatterns = [
    path("", include(router.urls)),
    path("debates/<pk>/start_or_continue/", StartOrContinueDebateView.as_view(), name="start_or_continue_debate"),
]
