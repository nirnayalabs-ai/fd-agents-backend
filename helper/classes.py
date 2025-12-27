from __future__ import annotations
import os
import threading
from typing import Any, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, AIMessage

load_dotenv()


class LLMModel(ChatGroq):

    def __init__(self, model_name: str = "llama-3.3-70b-versatile", api_key: str = os.environ.get("GROQ_API_KEY"), project_id: str = None, debate_id: str = None, agent_id: str = None) -> None:
        super().__init__(model=model_name, api_key=api_key)

        object.__setattr__(self, "model", model_name)
        object.__setattr__(self, "project_id", project_id)
        object.__setattr__(self, "debate_id", debate_id)
        object.__setattr__(self, "agent_id", agent_id)


    def log_the_interaction(self, input : list[BaseMessage] | str, response : AIMessage, agent_id: Optional[str] = None, org_id : str = None):
        input_messages = []
        metadata = response.usage_metadata

        if isinstance(input, list):
            for message in input:
                input_messages.append({
                    "type": message.type,
                    "content": message.content
                })
        else:
            input_messages.append({
                "type": "user",
                "content": input
            })
        from core_app import serializers

        data = {
            "project": self.project_id,
            "debate": self.debate_id,
            "agent": agent_id,
            "model_name": self.model,
            "metadata": metadata,
            "input_messages": input_messages,
            "output_response": response.content,
            "status" : "success"
        }
        if org_id:
            data['org'] = org_id
        serializer = serializers.LLMModelLogSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

    def invoke_with_log(self, input : Any, agent_id : str = None, org_id : str = None) -> Any:
        response = super().invoke(input)

        # Log the interaction
        try:
            self.log_the_interaction(input, response, agent_id, org_id)
        except Exception as e:
            print(f"Error logging LLM interaction: {e}")
        return response


class ContextStorage:
    """Thread-safe storage for request-scoped data."""

    def __init__(self):
        self._storage = threading.local()
        self._initialize_storage()

    def _initialize_storage(self):
        """Initialize storage dict if not present."""
        if not hasattr(self._storage, "data"):
            self._storage.data = {}

    def store(self, key: str, value: Any):
        """Store ANY Python object in thread-local storage."""
        self._initialize_storage()
        self._storage.data[key] = value

    def retrieve(self, key: str, default: Optional[Any] = None) -> Any:
        """Retrieve ANY Python object."""
        self._initialize_storage()
        return self._storage.data.get(key, default)

    # ------------------------------------------------------------------
    # USER (No User import needed — stores runtime instance)
    # ------------------------------------------------------------------
    def set_current_user(self, user: Any):
        self.store("current_user", user)

    def get_current_user(self, default=None):
        return self.retrieve("current_user", default)

    # ------------------------------------------------------------------
    # ORGANIZATION (Same — no Organization import needed)
    # ------------------------------------------------------------------
    def set_current_org(self, org: Any):
        self.store("current_org", org)

    def get_current_org(self, default=None):
        return self.retrieve("current_org", default)

    # ------------------------------------------------------------------
    def show(self):
        self._initialize_storage()
        print(self._storage.data)

    def clear(self):
        self._storage.data = {}
   
        
# class TrimMessages:
#     """Class to trim messages based on token limits, optimized for latency and memory."""
    
#     # Load spaCy model once and use its tokenizer for faster tokenization.
#     nlp = spacy.load("en_core_web_md")
#     tokenizer = nlp.tokenizer  # Use only the tokenizer to speed things up.
    
#     @classmethod
#     def trim(cls, messages : list[BaseMessage], token_limit=4500):
#         """
#         Trim a list of message objects to ensure their combined tokens do not exceed the token limit.
#         If a message exceeds the remaining tokens, modify its content in-place to include only the
#         tokens that fit within the limit, handling punctuation to avoid unnecessary spaces.        
#         """
#         total_tokens = 0
#         trimmed_messages = []
        
#         for message in messages:
#             # Use only the tokenizer to avoid overhead of full NLP pipeline.
#             doc = cls.tokenizer(message.content)
#             num_tokens = len(doc)
            
#             # If the entire message fits within the limit, use it as is.
#             if total_tokens + num_tokens <= token_limit:
#                 trimmed_messages.append(message)
#                 total_tokens += num_tokens
#             else:
#                 # Determine how many tokens we can still add.
#                 remaining_tokens = token_limit - total_tokens
#                 if remaining_tokens > 0:
#                     tokens = doc[:remaining_tokens]
#                     # Build the trimmed content token by token.
#                     trimmed_content = tokens[0].text
#                     for token in tokens[1:]:
#                         # Avoid inserting an extra space before punctuation.
#                         if token.is_punct:
#                             trimmed_content += token.text
#                         else:
#                             trimmed_content += " " + token.text
#                     # Modify the message object in place.
#                     message.content = trimmed_content
#                     trimmed_messages.append(message)
#                     total_tokens += remaining_tokens
#                 break  # Stop processing further messages as the token limit is reached.
        
#         return trimmed_messages