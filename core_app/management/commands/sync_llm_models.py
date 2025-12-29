from django.core.management.base import BaseCommand
from django.db import transaction

from orgs_app.models import LLMProvider, LLMModel
from helper.consonants import LLM_REGISTRY


class Command(BaseCommand):
    help = "Sync LLM Providers and Models from registry"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("🔄 Syncing LLM Providers & Models...")

        # Track existing models to deactivate removed ones later
        existing_models = {
            (m.provider.name, m.model_key): m
            for m in LLMModel.objects.select_related("provider")
        }

        active_model_keys = set()

        # Sync providers and models
        for provider_name, provider_data in LLM_REGISTRY.items():
            provider, _ = LLMProvider.objects.update_or_create(
                name=provider_name,
                defaults={
                    "is_active": provider_data.get("is_active", True),
                },
            )

            for model_data in provider_data.get("models", []):
                key = (provider_name, model_data["model_key"])
                active_model_keys.add(key)

                LLMModel.objects.update_or_create(
                    provider=provider,
                    model_key=model_data["model_key"],
                    defaults={
                        "display_name": model_data["display_name"],
                        "context_length": model_data.get("context_length"),
                        "is_active": model_data.get("is_active", True),
                    },
                )

        # Deactivate models removed from registry
        for key, model in existing_models.items():
            if key not in active_model_keys:
                if model.is_active:
                    model.is_active = False
                    model.save(update_fields=["is_active"])

        self.stdout.write(self.style.SUCCESS("✅ LLM sync completed successfully"))
