# Quickstart

## 1. Scan a repository

```bash
attackmap analyze /path/to/repo --output reports
```

AttackMap auto-detects the languages in the repo, runs the relevant analyzers,
and writes its results to `reports/`.

## 2. Read the results

The most useful artifacts:

| File | What it is |
| --- | --- |
| `reports/defensive-review.md` | Human-readable heuristic review |
| `reports/attackmap-report.json` | The full structured report (findings, surfaces, paths, exploitability) |
| `reports/*.md` sub-reports | Attack surface, attack paths, exploitability, diagrams |

## 3. Add dependency CVEs

```bash
attackmap analyze /path/to/repo --output reports --cve
```

Cross-references your dependencies against [OSV.dev](https://osv.dev) and folds
vulnerable packages into exploitability scoring (results cached for 24h).

## 4. Add an AI review

```bash
attackmap analyze /path/to/repo --output reports --llm
```

Generates a narrative defensive review with Claude (or OpenAI — see
[AI review](llm.md)). Every claim cites real evidence IDs, so the model can't
invent findings. Set an API key or sign in to the `claude` / `codex` CLI first.

## 5. Gate a pull request

Compare against a baseline and fail CI if new high-severity findings appear:

```bash
attackmap analyze . --baseline prev/attackmap-report.json \
  --diff-output reports/attackmap-diff.md --fail-on-new-high
```

See [CI & pull requests](ci.md) for the GitHub Action and PR bot.

## 6. Scan a fleet

Pass more than one repository to analyze a set of services together and surface
the bugs that live in the **seams** between them:

```bash
attackmap analyze ./service-a ./service-b ./gateway --output reports
```

Each repo gets its own `reports/<repo>/`, plus a `reports/fleet-summary.md` that
links callers to the routes they hit and flags cross-boundary flows,
trust-assumption gaps, and cross-repo anomalies. See
[Cross-repo fleet analysis](scanning.md#cross-repo-fleet-analysis).

## 7. Widen the net (recall)

`--recall` widens taint discovery and enumerates capability-reach, marking the
extra reach speculative; pair it with the verifier to adjudicate:

```bash
attackmap analyze . --recall --hunt --verify
```

See [Recall mode](scanning.md#recall-mode).
