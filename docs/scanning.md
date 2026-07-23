# Scanning & output

## The analyze command

```bash
attackmap analyze <path> [options]
```

`<path>` is the repository root. By default AttackMap resolves which analyzers
to run from the languages it finds, writes `all` output formats, and shows a
live progress bar when stderr is a terminal.

Pass two or more paths for a **fleet scan** (see [below](#cross-repo-fleet-analysis)).

Common options (full list in the [CLI reference](cli.md)):

- `--output <dir>` — where artifacts are written (default: current directory).
- `--format {all,markdown,json}` — which output formats to emit.
- `--module <name>` — restrict to specific analyzers (repeatable). See [Analyzers](analyzers.md).
- `--cve` — cross-reference dependencies against OSV.dev.
- `--recall` — widen taint discovery (see [Recall mode](#recall-mode)).
- `--progress-format {auto,json,none}` — `json` emits newline-delimited progress events on stderr for tool/GUI front-ends.

## Output artifacts

A scan writes a monolithic report plus focused sub-artifacts:

- **`attackmap-report.json`** — the canonical structured report. Contains findings (with stable IDs), attack surfaces, attack paths, exploitability scores, dependencies, and taint chains.
- **`defensive-review.md`** and the other Markdown sub-reports — human-readable views.
- **LLM artifacts** (only with the AI modes) — `defensive-review-llm.md`, `vulnerability-hypotheses.md`, `triage.md` (`--triage`), `remediation.md`, each with a `.meta.json` recording the backend, model, and token usage.
- **Fleet artifacts** (multi-repo runs) — `fleet-summary.md` / `.json` and `fleet-graph.md`, alongside each repo's own `<output>/<repo>/` report directory.

Findings carry **stable IDs**, which is what makes baseline diffing reliable.

## Anomaly & invariant mining

Beyond signature detectors, AttackMap compares the code against itself. The
**anomaly** pass flags the odd-one-out among sibling routes in a resource cohort
— the handler missing the auth, validation, or method norm its peers establish.
**Invariant mining** goes further and is signature-free: it infers an implicit
rule from repeated structure — e.g. "handlers that reach a database sink apply
an auth/validation guard *before* it" — and flags the site that violates the
mined invariant, citing the rule as evidence. Both are threshold-gated:
confidence scales with how consistent the cohort is, and a genuinely-split
surface isn't nagged.

## Recall mode

Aggressiveness is only useful *behind* a verifier. `--recall` widens the taint
walk — deeper import-hop depth and **capability-reach enumeration** (every place
data reaches a powerful capability: exec, filesystem, network, deserialize,
template, SQL — even with no known-bad pattern) — and marks the extra reach
**speculative** rather than asserting it. Speculative findings carry downgraded
confidence, are kept **out of `--fail-on-new-high`**, and are filtered from the
asserted exploitability/BOLA/attack-path passes. Pair it with `--hunt --verify`
to widen the net and then adjudicate what it catches:

```bash
attackmap analyze . --recall --hunt --verify
```

Default (non-recall) behavior is unchanged.

## Cross-repo fleet analysis

Pass two or more repositories and AttackMap scans a whole fleet — the
highest-value *unknown* bugs live at the **seams between services**, invisible to
any single-repo scan:

```bash
attackmap analyze ./service-a ./service-b ./gateway --output reports
```

Each repo is scanned independently into `reports/<repo>/`, then AttackMap:

- **links contracts** — matches one repo's outbound HTTP calls to another repo's
  routes (by normalized path template + method) into a repo-to-repo service
  graph (`fleet-graph.md`);
- flags **cross-boundary (confused-deputy) flows** — a value one repo forwards
  that the callee trusts into a dangerous sink or an unguarded object access;
- flags **trust-assumption gaps** — a state-changing call to a route the callee
  serves with no auth control, where each side assumes the other enforces;
- flags **cross-repo anomalies** — the sibling service that omits an auth control
  its peers enforce on the same route.

All cross-repo findings are **speculative** (a route may be protected by a
gateway/mTLS the heuristics can't see) and cite both sides; a `fleet-summary.md`
/ `.json` indexes the run. Single-repo behavior is unchanged.

## CI workflow security

Every scan also inspects `.github/workflows/*.yml` — a real attack surface that
static app scanners usually miss — and raises findings for supply-chain and
code-execution risks:

| Issue | What it catches | Severity |
| --- | --- | --- |
| Script injection | An attacker-controlled context (`github.event.*.{title,body,message,…}`, `github.head_ref`) interpolated into a `run:` step, so a crafted issue/PR title runs arbitrary shell. | High |
| `pull_request_target` + PR checkout | Building untrusted fork code with the base repo's secrets in scope. | High |
| Unpinned action | `uses: org/action@tag\|branch` instead of a pinned commit SHA. | Medium (branch) / Low (semver tag) |
| Secret in `run:` | `${{ secrets.* }}` expanded into a shell step — pass it via `env:` instead. | Medium |
| Over-broad permissions | `permissions: write-all` at the workflow or job level. | Medium |
| Self-hosted runner on PR | A self-hosted runner reachable from `pull_request`/`pull_request_target`. | High / Medium |

A hardened workflow — SHA-pinned actions, scoped `permissions:`, secrets via
`env:`, no untrusted-context interpolation — produces nothing. These findings
flow through SARIF, the diff gate, and [suppression](ci.md#suppressing-findings)
like any other.

## Unauthenticated state-changing routes

Raw auth signals are noisy — a large repo emits hundreds. AttackMap fuses them
into one conclusion: the public, state-changing (`POST/PUT/PATCH/DELETE`) routes
with **no authentication control on their own chain**. The control is resolved
*per route* — an Express middleware argument or global `app.use`, a FastAPI
`Depends(...)` / auth decorator / router dependency, a Spring `@PreAuthorize` /
`@Secured` — so a route doesn't inherit a neighbor's auth code. Routes behind a
control produce nothing, and the sensitive categories (webhook, admin, upload,
auth) keep their own findings. Each evidence line names the route and the
resolved chain.

## Baseline diffing & PR gating

Compare a fresh scan against a prior report to see what changed:

```bash
attackmap analyze . \
  --baseline prev/attackmap-report.json \
  --diff-output reports/attackmap-diff.md \
  --fail-on-new-high
```

- `--baseline <report.json>` — a prior `attackmap-report.json` to diff against.
- `--diff-output <file>` — where to write the Markdown diff (new / persisted / resolved).
- `--fail-on-new-high` — exit non-zero if the diff introduces any new HIGH-severity finding. Requires `--baseline`.

`--pr-comment <file>` writes a Markdown PR summary (diff + top exploitability)
for a bot to post. See [CI & pull requests](ci.md).
