# AttackMap

**Local-first defensive security analysis for real codebases.**

AttackMap reads a repository the way an attacker would — mapping its attack
surface, tracing tainted data to dangerous sinks, scoring exploitability, and
(optionally) having an LLM reason over the whole evidence pack. Everything runs
on your machine; nothing is uploaded unless you explicitly enable an LLM backend.

![AttackMap macOS app — scan overview](img/screenshots/04-overview.png)

*The macOS app after scanning OWASP Juice Shop — 29 findings, 22 exploitable sinks, and the single most exploitable route→sink path ranked first. See the [macOS app](gui.md#screenshots) page for the full walkthrough.*

```bash
brew install mlaify/tap/attackmap
attackmap analyze /path/to/repo --output reports
```

## What it does

- **Attack-surface mapping** — routes, entry points, exposure, and auth signals across many languages.
- **Taint analysis** — import-graph data-flow from untrusted sources to injection sinks (SQLi, SSRF, SSTI, deserialization, and more), with **sanitizer awareness**: a chain that passes through a known escaper/validator/binder (`shlex.quote`, `secure_filename`, `is_safe_url`, driver escapers, …) is downgraded instead of firing a false positive.
- **Anomaly & invariant mining** — the odd-one-out among sibling routes, plus signature-free **invariant mining**: a handler that reaches a dangerous sink without the guard its peers apply.
- **Exploitability scoring** — fuses signals (including CVEs on the path) into a ranked, honest view of what matters.
- **Dependency CVEs** — cross-reference your SBOM against [OSV.dev](https://osv.dev) (`--cve`).
- **AI review + verify jury** — narrative defensive review and vulnerability-hypothesis hunting adjudicated against cited source, scaling into a jury (`--verify-votes` / `--hunt-lenses` / `--hunt-rounds`), plus remediation and triage (`--llm` / `--hunt --verify` / `--remediate` / `--triage`).
- **Recall mode** — verifier-gated aggressive discovery (`--recall`): widens the taint walk and enumerates capability-reach, marking the extra reach speculative for the verifier to adjudicate.
- **Cross-repo / fleet analysis** — scan multiple services at once (`attackmap analyze repoA repoB …`) and surface the bugs in the seams: cross-boundary (confused-deputy) flows, trust-assumption gaps, and the sibling service that omits a control its peers enforce.
- **CI-friendly** — SARIF, a PR summary bot, and baseline diff gating.

!!! note "Status"
    AttackMap is **beta**. It's a precision-first heuristic tool — a strong
    lead generator and reviewer aid, not a substitute for manual review.

## Where to go next

- [Install](install.md) — Homebrew, pipx, pip, Docker, or the macOS app.
- [Quickstart](quickstart.md) — your first scan in two minutes.
- [AI review](llm.md) — Claude or OpenAI/Codex, and how auth resolves.
- [Analyzer SDK](sdk.md) — write your own ecosystem analyzer.
