# AttackMap

**Local-first defensive security analysis for real codebases.**

AttackMap reads a repository the way an attacker would — mapping its attack
surface, tracing tainted data to dangerous sinks, scoring exploitability, and
(optionally) having an LLM reason over the whole evidence pack. Everything runs
on your machine; nothing is uploaded unless you explicitly enable an LLM backend.

```bash
brew install mlaify/tap/attackmap
attackmap analyze /path/to/repo --output reports
```

## What it does

- **Attack-surface mapping** — routes, entry points, exposure, and auth signals across many languages.
- **Taint analysis** — import-graph data-flow from untrusted sources to injection sinks (SQLi, SSRF, SSTI, deserialization, and more).
- **Exploitability scoring** — fuses signals (including CVEs on the path) into a ranked, honest view of what matters.
- **Dependency CVEs** — cross-reference your SBOM against [OSV.dev](https://osv.dev) (`--cve`).
- **AI review** — narrative defensive review, vulnerability-hypothesis hunting, and remediation suggestions, grounded in cited evidence (`--llm` / `--hunt` / `--remediate`).
- **CI-friendly** — SARIF, a PR summary bot, and baseline diff gating.

!!! note "Status"
    AttackMap is **alpha**. It's a precision-first heuristic tool — a strong
    lead generator and reviewer aid, not a substitute for manual review.

## Where to go next

- [Install](install.md) — Homebrew, pipx, pip, Docker, or the macOS app.
- [Quickstart](quickstart.md) — your first scan in two minutes.
- [AI review](llm.md) — Claude or OpenAI/Codex, and how auth resolves.
- [Analyzer SDK](sdk.md) — write your own ecosystem analyzer.
