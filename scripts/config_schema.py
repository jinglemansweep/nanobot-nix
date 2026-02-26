"""Config schema for nanobot-nix.

This is the only file that needs updating when upstream config changes.
It contains no logic — only data.
"""

DEFAULTS = {
    "agents": {
        "defaults": {
            "model": "anthropic/claude-sonnet-4-5-20250514",
        },
    },
}

ENV_MAP = {
    "PROVIDERS_OPENROUTER_APIKEY": ("providers", "openrouter", "apiKey"),
    "PROVIDERS_OPENROUTER_APIBASE": ("providers", "openrouter", "apiBase"),
    "PROVIDERS_ANTHROPIC_APIKEY": ("providers", "anthropic", "apiKey"),
    "PROVIDERS_ANTHROPIC_APIBASE": ("providers", "anthropic", "apiBase"),
    "PROVIDERS_OPENAI_APIKEY": ("providers", "openai", "apiKey"),
    "PROVIDERS_DEEPSEEK_APIKEY": ("providers", "deepseek", "apiKey"),
    "PROVIDERS_GROQ_APIKEY": ("providers", "groq", "apiKey"),
    "PROVIDERS_ZHIPU_APIKEY": ("providers", "zhipu", "apiKey"),
    "PROVIDERS_ZHIPU_APIBASE": ("providers", "zhipu", "apiBase"),
    "PROVIDERS_CUSTOM_APIKEY": ("providers", "custom", "apiKey"),
    "PROVIDERS_CUSTOM_APIBASE": ("providers", "custom", "apiBase"),
    "AGENTS_DEFAULTS_MODEL": ("agents", "defaults", "model"),
    "CHANNELS_TELEGRAM_ENABLED": ("channels", "telegram", "enabled"),
    "CHANNELS_TELEGRAM_TOKEN": ("channels", "telegram", "token"),
    "CHANNELS_TELEGRAM_ALLOWFROM": ("channels", "telegram", "allowFrom"),
    "CHANNELS_DISCORD_ENABLED": ("channels", "discord", "enabled"),
    "CHANNELS_DISCORD_TOKEN": ("channels", "discord", "token"),
    "CHANNELS_DISCORD_ALLOWFROM": ("channels", "discord", "allowFrom"),
    "CHANNELS_SLACK_ENABLED": ("channels", "slack", "enabled"),
    "CHANNELS_SLACK_APPTOKEN": ("channels", "slack", "appToken"),
    "CHANNELS_SLACK_BOTTOKEN": ("channels", "slack", "botToken"),
    "CHANNELS_SLACK_ALLOWFROM": ("channels", "slack", "allowFrom"),
    "CHANNELS_WHATSAPP_ENABLED": ("channels", "whatsapp", "enabled"),
    "CHANNELS_WHATSAPP_ALLOWFROM": ("channels", "whatsapp", "allowFrom"),
    "TOOLS_WEB_SEARCH_APIKEY": ("tools", "web", "search", "apiKey"),
    "TOOLS_MCPSERVERS": ("tools", "mcpServers"),
}

ARRAY_FIELDS = {
    "CHANNELS_TELEGRAM_ALLOWFROM",
    "CHANNELS_DISCORD_ALLOWFROM",
    "CHANNELS_SLACK_ALLOWFROM",
    "CHANNELS_WHATSAPP_ALLOWFROM",
}

ALIASES = {
    "OPENROUTER_API_KEY": "NANOBOT_PROVIDERS_OPENROUTER_APIKEY",
    "ANTHROPIC_API_KEY": "NANOBOT_PROVIDERS_ANTHROPIC_APIKEY",
    "OPENAI_API_KEY": "NANOBOT_PROVIDERS_OPENAI_APIKEY",
    "DEEPSEEK_API_KEY": "NANOBOT_PROVIDERS_DEEPSEEK_APIKEY",
    "GROQ_API_KEY": "NANOBOT_PROVIDERS_GROQ_APIKEY",
    "NANOBOT_MODEL": "NANOBOT_AGENTS_DEFAULTS_MODEL",
    "TELEGRAM_BOT_TOKEN": "NANOBOT_CHANNELS_TELEGRAM_TOKEN",
    "BRAVE_SEARCH_API_KEY": "NANOBOT_TOOLS_WEB_SEARCH_APIKEY",
}
