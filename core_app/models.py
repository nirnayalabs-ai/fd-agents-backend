from django.db import models
from orgs_app.models import OrganizationFieldMixin
from helper.models import UUIDPrimaryKey, TimeLine, IsActiveModel

class Project(UUIDPrimaryKey, TimeLine, IsActiveModel, OrganizationFieldMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Agent(UUIDPrimaryKey, TimeLine, IsActiveModel, OrganizationFieldMixin):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="agents")

    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)         
    goal = models.TextField() 
    domain_expertise = models.TextField() 
    debate_style = models.TextField()                      
    backstory = models.TextField(blank=True, null=True)   
    category = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict)

    is_system_agent = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.name
    

class Debate(UUIDPrimaryKey, TimeLine, IsActiveModel, OrganizationFieldMixin):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="debates")
    
    name = models.CharField(max_length=255, null=True, blank=True)
    topic = models.TextField()                 
    summary = models.TextField(blank=True, null=True)
    final_dission = models.TextField(blank=True, null=True)

    agents = models.ManyToManyField(Agent, related_name="debates", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Debate on {self.topic[:50]}..."

    def agents_list(self):
        return "\n".join([f"- Name: {agent.name} Role: {agent.role} Goal: {agent.goal}" for agent in self.agents.all()])
    
    def debate_messages(self, return_queryset=False ):
        messages_qs = self.messages.filter(is_memory_disabled = False).order_by("order")
        if return_queryset:
            return messages_qs
        return "\n".join([f"{msg.content}" for msg in messages_qs])


class DebateMessage(UUIDPrimaryKey, TimeLine, OrganizationFieldMixin):
    debate = models.ForeignKey(Debate, on_delete=models.CASCADE, related_name="messages")
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="messages")

    content = models.TextField()
    order = models.PositiveIntegerField(blank=True, null=True)

    is_memory_disabled = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]
        unique_together = ("debate", "order")

    def save(self, *args, **kwargs):
        if self.order is None:
            last_message = (
                DebateMessage.objects
                .filter(debate=self.debate)
                .order_by("-order")
                .first()
            )
            if last_message:
                self.order = last_message.order + 1
            else:
                self.order = 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.agent.name} → {self.debate.id} (#{self.order})"
    

class LLMModelLog(UUIDPrimaryKey, OrganizationFieldMixin):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="llm_model_logs", blank=True, null=True)
    debate = models.ForeignKey(Debate, on_delete=models.CASCADE, related_name="llm_model_logs", blank=True, null=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="llm_model_logs", blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    model_name = models.CharField(max_length=255)
    input_messages = models.JSONField(default=list)
    output_response = models.TextField()
    status = models.CharField(max_length=50)
    metadata = models.JSONField(default=dict) # token_usage, response_time, etc.
