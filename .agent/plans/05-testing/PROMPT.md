# Various Startup Errors

```
gateway-1  | INFO: Processed 5 env var(s), skipped 0 unknown key(s), resolved 0 alias(es)
gateway-1  | INFO: Config written to /root/.nanobot/config.json
gateway-1  | 🐈 Starting nanobot gateway on port 18790...
gateway-1  | Warning: Failed to load config from /root/.nanobot/config.json: 1 validation error for Config
gateway-1  | channels.discord.allowFrom
gateway-1  |   Input should be a valid list [type=list_type, input_value=701044353249837097, input_type=int]
gateway-1  |     For further information visit https://errors.pydantic.dev/2.12/v/list_type
gateway-1  | Using default configuration.
gateway-1  | Error: No API key configured.
gateway-1  | Set one in ~/.nanobot/config.json under providers section
````

Env file includes:

```
NANOBOT_CHANNELS_DISCORD_ENABLED=true
NANOBOT_CHANNELS_DISCORD_TOKEN=<redacted>
NANOBOT_CHANNELS_DISCORD_ALLOWFROM=123444351234838888 # randomized for security
NANOBOT_PROVIDERS_ZHIPU_APIBASE=https://api.z.ai/api/coding/paas/v4
NANOBOT_PROVIDERS_ZHIPU_APIKEY=<obfuscated>
```