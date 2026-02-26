# Research

> Source: `.agent/plans/04-testing-02/PROMPT.md`

## Zhipu AI / Z.AI / GLM

- **URL:** https://z.ai (International), https://open.bigmodel.cn (China)
- **Documentation:** https://docs.z.ai/api-reference/introduction
- **Status:** Actively maintained, major provider with multiple model generations
- **Latest Version:** GLM-5 (newest), GLM-4.7 (flagship coding model), GLM-4.6, GLM-4.5 series
- **Compatibility:** OpenAI-compatible API. Supports standard `/chat/completions` endpoint, Bearer token auth, streaming, and function/tool calling.
- **Key Findings:**
  - Two API base URLs depending on region:
    - International: `https://api.z.ai/api/paas/v4/`
    - China: `https://open.bigmodel.cn/api/paas/v4/`
  - Coding Plan subscribers use a separate base path: `https://api.z.ai/api/coding/paas/v4` (this is the most common use case and the chosen default for this project)
  - Authentication uses standard Bearer token: `Authorization: Bearer YOUR_API_KEY`
  - API key format is a two-part hexadecimal/alphanumeric string (different from OpenAI's `sk-` prefix)
  - OpenAI SDK can be used directly by setting `base_url` to the Zhipu endpoint
  - Models are referenced by ID: `glm-5`, `glm-4.7`, `glm-4.6`, `glm-4.5`, `glm-4.5-air`, `glm-4-plus`, etc.
  - Free tier models available: `glm-4.7-flash`, `glm-4.5-flash`, `glm-4.6v-flash`
  - GitHub organization: `zai-org`
- **Concerns:**
  - Strict validation: rejects empty `text` fields in message content arrays (unlike OpenAI which tolerates them). Error: `messages[N].content[N].text:不能为空`
  - No parallel tool calls supported on GLM-4.5 series
  - No prompt caching support
  - China and international platforms are separate — API keys may not be interchangeable
  - Overseas pricing significantly higher than domestic, with recent price increases (Feb 2026)
