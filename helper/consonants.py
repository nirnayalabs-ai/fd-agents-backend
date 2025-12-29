LLM_REGISTRY = {
    "groq": {
        "is_active": True,
        "models": [
            {
                "model_key": "qwen/qwen3-32b",
                "display_name": "Qwen 3 – 32B",
                "context_length": 32768,
                "is_active": True,
            },
            {
                "model_key": "llama-3.1-8b-instant",
                "display_name": "LLaMA 3.1 – 8B Instant",
                "context_length": 8192,
                "is_active": True,
            },
            {
                "model_key": "llama-3.3-70b-versatile",
                "display_name": "LLaMA 3.3 – 70B Versatile",
                "context_length": 32768,
                "is_active": True,
            },
            {
                "model_key": "meta-llama/llama-4-scout-17b-16e-instruct",
                "display_name": "LLaMA 4 Scout – 17B",
                "context_length": 16384,
                "is_active": True,
            },
            {
                "model_key": "openai/gpt-oss-120b",
                "display_name": "GPT-OSS – 120B",
                "context_length": 32768,
                "is_active": True,
            },
            {
                "model_key": "openai/gpt-oss-20b",
                "display_name": "GPT-OSS – 20B",
                "context_length": 16384,
                "is_active": True,
            },
        ],
    },

    "openai": {
        "is_active": True,
        "models": [
            {"model_key": "gpt-5.2", "display_name": "GPT-5.2", "context_length": 128000, "is_active": True},
            {"model_key": "gpt-5.1", "display_name": "GPT-5.1", "context_length": 128000, "is_active": True},
            {"model_key": "gpt-5", "display_name": "GPT-5", "context_length": 128000, "is_active": True},
            {"model_key": "gpt-5-mini", "display_name": "GPT-5 Mini", "context_length": 64000, "is_active": True},
            {"model_key": "gpt-5-nano", "display_name": "GPT-5 Nano", "context_length": 32000, "is_active": True},
            {"model_key": "gpt-4.1", "display_name": "GPT-4.1", "context_length": 128000, "is_active": True},
            {"model_key": "gpt-4.1-mini", "display_name": "GPT-4.1 Mini", "context_length": 64000, "is_active": True},
            {"model_key": "gpt-4o", "display_name": "GPT-4o", "context_length": 128000, "is_active": True},
            {"model_key": "gpt-4o-mini", "display_name": "GPT-4o Mini", "context_length": 64000, "is_active": True},
        ],
    },

    "gemini": {
        "is_active": True,
        "models": [
            {"model_key": "gemini-3-pro-preview", "display_name": "Gemini 3 Pro (Preview)", "context_length": 128000, "is_active": True},
            {"model_key": "gemini-3-flash-preview", "display_name": "Gemini 3 Flash (Preview)", "context_length": 64000, "is_active": True},
            {"model_key": "gemini-2.5-pro", "display_name": "Gemini 2.5 Pro", "context_length": 128000, "is_active": True},
            {"model_key": "gemini-2.5-flash", "display_name": "Gemini 2.5 Flash", "context_length": 64000, "is_active": True},
            {"model_key": "gemini-2.5-flash-lite", "display_name": "Gemini 2.5 Flash Lite", "context_length": 32000, "is_active": True},
            {"model_key": "gemini-2.0-flash", "display_name": "Gemini 2.0 Flash", "context_length": 32000, "is_active": True},
        ],
    },
}
