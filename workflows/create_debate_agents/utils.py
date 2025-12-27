from config import context_storage

from core_app.models import DebateMessage, Agent, Debate
from core_app.serializers import DebateMessageSerializer


def create_debate_message(content: str, debate: Debate, agent: Agent) -> DebateMessage:
    data = {
        "debate" : debate.id,
        "agent" : agent.id,
        "content" : content
    }

    serializer = DebateMessageSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.instance