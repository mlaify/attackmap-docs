# AI review (LLM)

AttackMap can hand its structured evidence pack to an LLM. Every claim must cite
real surface/asset/control IDs, so the model reasons over grounded evidence
rather than inventing findings. All LLM modes are **opt-in**.

## Modes

| Flag | What it produces |
| --- | --- |
| `--llm` | A narrative defensive review (`defensive-review-llm.md`). |
| `--hunt` | Ranked, human-verifiable **exploit-chain hypotheses** — leads, not detections (`vulnerability-hypotheses.md`). |
| `--hunt --verify` | Adjudicates each hypothesis against the cited source: CONFIRMED / REFUTED / NEEDS REVIEW. |
| `--remediate` | Review-first fix suggestions per finding (`remediation.md`). |

!!! warning "Hunt output is hypotheses, not detections"
    `--hunt` produces leads a human must confirm. It won't assign CVEs or emit
    exploit code, and each lead lists exactly what to verify.

## Providers

Choose with `--llm-provider`:

- **`claude`** (default) — Anthropic. Default model `claude-opus-4-8`.
- **`openai`** — OpenAI / Codex. Default model `gpt-5-codex`.

`--llm-model` passes any model ID through verbatim, so you're never limited to a
hardcoded list.

## Backends & credentials

Each provider resolves a backend automatically (`--llm-backend auto`), or you can
force `api` / `cli`:

=== "Claude"

    1. `ANTHROPIC_API_KEY` → API (per-token billing)
    2. `ANTHROPIC_AUTH_TOKEN` → API (OAuth bearer)
    3. the `claude` CLI → your Claude subscription (`claude login`)

=== "OpenAI"

    1. `OPENAI_API_KEY` → the Responses API
    2. the `codex` CLI → your Codex subscription (`codex login`)

The API backends need the LLM extra (`pip install "attackmap[llm]"`); the CLI
backends just need `claude` / `codex` on your `PATH`.

## Tuning

- `--llm-effort {low,medium,high,xhigh,max}` — reasoning effort (default `high`). For OpenAI, `xhigh`/`max` clamp to `high`.
- `--llm-speed {standard,fast}` — Fast mode (~2.5× output) on Claude Opus 4.8/4.7 via the API backend; ignored elsewhere.

## Example

```bash
# Claude, subscription CLI, hunt + verify:
attackmap analyze . --hunt --verify

# OpenAI Codex via API, remediation:
export OPENAI_API_KEY=sk-...
attackmap analyze . --remediate --llm-provider openai --llm-model gpt-5-codex
```
