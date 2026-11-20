# ADR-009: BYOK Provider Abstraction for LLM Inference

- **Status**: Accepted
- **Date**: 2026-11-20
- **Authors**: Technical Lead, Architecture Engineer

---

## 1. Context
The platform offers advanced conversational career discovery, goal extraction, and resume critique. To keep the open-source platform free to run without incurring unsustainable LLM API bills, we need a sustainable inference strategy that preserves user choice and privacy.

## 2. Decision
Implement a **Bring Your Own Key (BYOK)** LLM provider abstraction:
1. Candidates configure their personal API keys from supported providers:
   - NVIDIA NIM
   - Cloudflare Workers AI
   - OpenRouter
   - Google Gemini
2. Candidate API keys are encrypted at rest using AES-256-GCM authenticated envelope encryption in Supabase.
3. The backend abstracts LLM interactions behind a unified `LLMClient` protocol, ensuring agent workflows in LangGraph remain agnostic to the specific underlying model provider.

## 3. Alternatives Considered
- **Centralized Platform API Key**: Funding all user queries through a central developer API key. Rejected due to high ongoing cost liability and vulnerability to denial-of-wallet attacks.
- **Single Provider Lock-in (e.g. OpenAI only)**: Rejected; Indian candidates frequently use diverse free/credit allowances (NVIDIA NIM free tiers, Gemini API free tier, Cloudflare Workers AI free daily quota).

## 4. Consequences
- **Positive**: Zero platform API token liability, candidate owns their data and model choice, resilient against single-provider outages.
- **Negative**: User onboarding requires acquiring and pasting an API key; candidate model capabilities may vary in reasoning quality.

## 5. Risks
- Key theft. Mitigated by AES-256-GCM encryption at rest, memory-only decryption, and zero logging of key parameters.

## 6. References
- [docs/SECURITY.md](../SECURITY.md)
