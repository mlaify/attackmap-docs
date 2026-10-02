# Analyzer SDK

An analyzer is a small Python package that inspects a repository and returns
structured signals: routes, outbound calls, databases and hints, each with a
file and line. AttackMap discovers analyzers through a Python **entry point**,
so your plugin is a package that advertises itself. Core doesn't need to change.

!!! info "Canonical contract"
    The authoritative contract is the `attackmap.sdk` package in the
    [engine repo](https://github.com/mlaify/AttackMap) (`src/attackmap/sdk/`).
    Anything you can import from `attackmap.sdk` is stable across minor
    releases. Anything else in `attackmap` is internal. If this page and the
    repo disagree, the repo is correct.

!!! warning "Version note"
    Run order by `priority`, opt-in `enabled_by_default=False`, failure
    isolation (`analyzer_errors`, `--strict-analyzers`) and the
    `attackmap.sdk.fs` helpers are on core `main` and ship in the first release
    after **v0.4.31**. On v0.4.31 and earlier, built-ins always run first,
    `priority` and `enabled_by_default` are ignored, an analyzer that raises
    aborts the whole scan, and `attackmap.sdk.fs` doesn't exist.

## A complete example

This analyzer finds Flask `@app.route(...)` decorators. It loads and runs
against core as written; the docs repo has a test that extracts this block and
runs it.

```python title="my_package/analyzer.py"
import re
from pathlib import Path

from attackmap.sdk import (
    AnalyzerMetadata,
    AnalyzerResult,
    FrameworkHint,
    Route,
    iter_repo_files,
    line_of,
    line_snippet,
    read_source,
    rel,
)

_ROUTE = re.compile(
    r"""@\w+\.route\(\s*["']([^"']+)["']"""
    r"""(?:[^)]*methods\s*=\s*\[([^\]]*)\])?"""
)
_MANIFESTS = {"requirements.txt", "pyproject.toml", "setup.cfg", "Pipfile"}


class FlaskLiteAnalyzer:
    metadata = AnalyzerMetadata(
        name="flask-lite",  # slug; also the entry-point key and the -m value
        display_name="Flask Lite",
        version="0.1.0",  # your plugin's version, not attackmap's
        description="Detects Flask @app.route handlers.",
        scope="Small Flask services.",
        languages=["python"],
        targets=["flask"],
        priority=100,  # framework analyzers use 50-149; lower runs first
        experimental=True,
        enabled_by_default=False,  # opt-in: runs only with -m flask-lite
    )

    @property
    def name(self) -> str:
        # Required: core rejects an analyzer without a non-empty `name`.
        return self.metadata.name

    def detect(self, root: str | Path) -> bool:
        # Cheap check: does a manifest mention flask?
        for path in iter_repo_files(root, names=_MANIFESTS):
            text = read_source(path, root=root)
            if text and "flask" in text.lower():
                return True
        return False

    def analyze(self, root: str | Path) -> AnalyzerResult:
        root = Path(root)
        result = AnalyzerResult(root=str(root), languages=["python"])
        for path in iter_repo_files(root, suffixes={".py"}, include_tests=False):
            text = read_source(path, root=root)
            if text is None:  # unreadable or binary: skip, never raise
                continue
            result.files_scanned += 1
            file = rel(path, root)
            for match in _ROUTE.finditer(text):
                line = line_of(text, match.start())
                methods = [
                    m.strip(" '\"").upper()
                    for m in (match.group(2) or "").split(",")
                    if m.strip(" '\"")
                ] or ["GET"]
                for method in methods:
                    result.routes.append(
                        Route(path=match.group(1), method=method, file=file, line=line)
                    )
                result.framework_hints.append(
                    FrameworkHint(
                        hint="flask",
                        file=file,
                        line=line,
                        evidence_text=line_snippet(text, line),
                    )
                )
        return result
```

An analyzer needs four things (`AnalyzerProtocol`):

| Member | Purpose |
|---|---|
| `metadata: AnalyzerMetadata` | Static description; see [the field table](#analyzermetadata-fields). |
| `name` (property or attribute) | Non-empty string, normally `metadata.name`. Without it the plugin is skipped with *loaded object is not a valid analyzer*. |
| `detect(root) -> bool` | Should this analyzer run on this repo? Keep it cheap. If it raises, the analyzer is treated as not matching and a warning is logged. |
| `analyze(root) -> AnalyzerResult` | Extract signals and return them. |

The entry point may name the class, a zero-argument factory or an instance.
Core instantiates a class with no arguments.

## Register the entry point

Advertise the analyzer under the **`attackmap.analyzers`** group in your
package's `pyproject.toml`:

```toml
[project.entry-points."attackmap.analyzers"]
flask-lite = "my_package.analyzer:FlaskLiteAnalyzer"
```

Install the package into the same environment as AttackMap. It then appears in
`attackmap modules` and can be selected with `-m flask-lite`. If it doesn't
appear, look for a warning from the `attackmap.analyzers` logger: failing to
load, invalid metadata and a missing `name` each log why the plugin was skipped
(`Failed to ...` or `Skipping entry point ...`).

## `AnalyzerMetadata` fields

From the pydantic `Field` descriptions in `attackmap/analyzer_contracts.py`.
Adding fields is a minor-release change; removing or renaming one is a
major-version break.

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | required | Slug identifier. Must match `[a-z0-9][a-z0-9-]*`. The entry-point key AttackMap uses to select the analyzer (e.g. from `--module`) and to attribute signals via provenance. |
| `display_name` | `str` | `name` | Human-friendly name shown in `attackmap modules` output and reports. |
| `version` | `str` | `"0.1.0"` | Semver of the analyzer plugin itself, not attackmap. Should match your package's `pyproject.toml` version. Must not be empty. |
| `description` | `str` | `""` | One-sentence summary of what the analyzer detects. Shown in module listings. |
| `scope` | `str` | `""` | One sentence on the kinds of repositories this analyzer targets (e.g. "Node/TypeScript backend service repos"). |
| `targets` | `list[str]` | `[]` | Frameworks, protocols or platform tokens the analyzer specializes in (e.g. `["react-native", "expo"]`). Combined with `languages` to compute `ecosystems`. |
| `languages` | `list[str]` | `[]` | Programming languages the analyzer parses (e.g. `["javascript", "typescript"]`). Combined with `targets` to compute `ecosystems`. |
| `priority` | `int` (≥ 0) | `100` | Run order across built-ins and plugins: lower runs first, ties broken by name. Merge is first-seen-wins in that order, so a lower value also wins a duplicate signal. Convention: 0–49 broad language analyzers, 50–149 framework analyzers, 150+ app-specific analyzers. |
| `experimental` | `bool` | `True` | Whether the analyzer is still stabilizing. Doesn't affect execution, only how core presents it in listings. Experimental analyzers should normally leave `enabled_by_default` False. |
| `enabled_by_default` | `bool` | `False` | Whether to run without an explicit `--module`. False makes it opt-in; see [Opt-in analyzers](#opt-in-analyzers). Broad language analyzers set it True; specialty framework and app analyzers usually leave it False. |

`metadata.ecosystems` is a read-only, de-duplicated, lowercased tuple of
`languages` + `targets`. The legacy `ecosystems=` constructor argument is still
accepted and used as `languages` when neither `languages` nor `targets` is set.

## What `analyze` returns

`AnalyzerResult` **is** `ScanResult`: the SDK exports it as an alias, so
`AnalyzerResult is ScanResult` is true and either name works. `root` is the
only required field. Fill in the signal lists below and `files_scanned`, and
optionally `languages` and `limitations` (strings describing what you couldn't
analyze).

Returning a plain `dict` also works: core validates it as a `ScanResult`.
Returning anything else (including `None`) counts as a failure; see
[Failure isolation](#failure-isolation).

### Signal models

All are exported from `attackmap.sdk`. Every model also has an optional
`source_analyzer` field, which core fills with your analyzer's `name` if you
leave it empty. `line` is 1-indexed and optional everywhere. `evidence_text`
is the source snippet that justifies the signal.

| `ScanResult` field | Model | Fields (required in **bold**) | Dedup key |
|---|---|---|---|
| `routes` | `Route` | **`path`**, `method` (default `"ANY"`), **`file`**, `line` | `(path, method, file)` |
| `external_calls` | `ExternalCall` | **`target`**, **`file`**, `line`, `method`, `evidence_text` | `(target, method, file)` |
| `databases` | `DatabaseHint` | **`kind`**, **`file`**, `line`, `evidence_text` | `(kind, file)` |
| `auth_hints` | `AuthHint` | **`hint`**, **`file`**, `line`, `evidence_text`, `confidence` (0.7) | `(hint, file)` |
| `service_hints` | `ServiceHint` | same as `AuthHint` | `(hint, file)` |
| `edge_hints` | `EdgeHint` | same as `AuthHint` | `(hint, file)` |
| `entrypoint_hints` | `EntrypointHint` | same as `AuthHint` | `(hint, file)` |
| `protocol_hints` | `ProtocolHint` | same as `AuthHint` | `(hint, file)` |
| `framework_hints` | `FrameworkHint` | same as `AuthHint` | `(hint, file)` |
| `secret_hints` | `SecretHint` | **`name`**, **`file`**, `line`, `evidence_text`, `confidence` (0.85), `kind` (`"env_reference"`) | `(name, file, line)` |
| `dependencies` | `DependencyHint` | **`name`**, **`version`**, **`ecosystem`** (`pypi`, `npm`, `go`, `cargo`, `composer` or `swiftpm`), **`file`**, `line`, `dev`, `resolved`, `direct`, `via`, `evidence_text` | `(ecosystem, name, version, file, dev)` |

`ScanResult` has other list fields too: `taint_chains`, `vulnerabilities`,
`authz_candidates`, `crypto_weaknesses`, `web_hardening_issues`,
`code_weaknesses`, `workflow_issues`, `anomalies` and `analyzer_errors`. Core
fills these itself from the merged signals, once per scan. They aren't part
of the analyzer contract, so leave them empty.

### What analyzers don't do

Analyzers emit **signals**, not conclusions. They don't produce findings,
severities, taint chains, attack paths or reports. Core owns all of that and
derives it from the merged signals. If you want a finding, emit a richer
signal and let core do the reasoning.

## How results are merged

Core runs every selected analyzer, stamps provenance, and merges the results
with `attackmap.analyzers.merge_analyzer_results`. The dedup keys come from
`attackmap.merge.MERGE_SCHEMA`.

- **Order.** Analyzers run in `(metadata.priority, name)` order, built-ins and
  plugins alike.
- **First seen wins.** Within each list field, a signal whose dedup key (the
  table above) was already seen is dropped. Because of the run order, the
  analyzer with the lower `priority` value wins a duplicate. To make your
  richer route replace a built-in's, give your analyzer a lower priority than
  that built-in (for example, the built-in `python-web` analyzer is 20).
- **Order is preserved.** Signals appear in the order they were first seen.
- **`languages`** is the sorted union, **`limitations`** the de-duplicated
  union, and **`files_scanned`** the sum.

Two analyzers that both emit `GET /items` in `app.py` produce one route in the
report, the one from whichever ran first.

## Opt-in analyzers

With no `-m/--module`, core runs every installed analyzer whose `detect()`
returns True, **except** those with `enabled_by_default=False`. Those are
opt-in: they run only when named with `-m`, and `detect()` still gates them.
When an opt-in analyzer matches a repo but isn't selected, the CLI says so:

```text
Opt-in analyzers match this repo but were not run: flask-lite. Enable with -m flask-lite.
```

Passing any `-m` switches to explicit selection: only the named analyzers are
considered (built-ins included only if named), opt-in or not.

## Failure isolation

If `analyze()` raises, or returns something other than a `ScanResult` or a
valid dict, core logs it, skips that analyzer and carries on with the rest.
The console prints `Analyzer '<name>' failed and was skipped: …`, and
`attackmap-report.json` lists it under `scan.analyzer_errors` with the
analyzer name, exception type and a redacted message.

Pass `--strict-analyzers` to fail fast instead. Use it while developing a
plugin and in CI, so a broken analyzer fails the run rather than silently
reducing coverage.

## Optional keyword arguments

Core calls `analyze(root)`. It passes two extra keyword arguments only if your
`analyze` signature declares them, so a plugin that doesn't know about them
keeps working:

- **`progress`** is passed when the CLI is showing progress. It's the scan's
  progress reporter; `progress.stage("label")` shows what your analyzer is
  doing. Don't call `progress.done()`, because core ends the scan. The type
  isn't part of the stable SDK, so treat it as optional and duck-typed.
- **`recall`** is passed as `True` only when the user ran `--recall`. Use it
  to surface lower-confidence signals you'd normally hold back.

```python
def analyze(self, root, progress=None, recall=False):
    if progress is not None:
        progress.stage("Flask routes")
    ...
```

## Walking and reading the repo

Use `attackmap.sdk.fs` (also re-exported from `attackmap.sdk`) rather than
`Path.rglob` and `read_text`:

| Helper | What it does |
|---|---|
| `iter_repo_files(root, *, suffixes=None, names=None, skip_dirs=DEFAULT_SKIP_DIRS, max_bytes=None, include_tests=True, on_skip=None)` | Yields regular files, sorted and depth-first. Filters by suffix (case-insensitive) or exact file name. Prunes `skip_dirs` by repo-relative directory name, never follows symlinks out of the repo, skips AttackMap's own output directories and files over the size cap. `include_tests=False` drops test, spec and fixture files. `on_skip(path, reason)` reports skipped symlinks and oversized files. |
| `read_source(path, *, root=None)` | Reads text as UTF-8 (with or without BOM), then cp1252, then latin-1. Returns `None` for unreadable or binary files and, with `root`, for paths outside it. Never raises. |
| `rel(path, root)` | `path` relative to `root`, POSIX-style. Use it for `file` fields. |
| `line_of(content, offset)` | 1-indexed line of a character offset, such as `match.start()`. |
| `line_snippet(content, line, max_len=200)` | The stripped text of a line, truncated, for `evidence_text`. |
| `DEFAULT_SKIP_DIRS` | The directories no analyzer should enter (`node_modules`, `.git`, `vendor`, build output and so on). Extend it with a set union for your ecosystem, e.g. adding `bin` and `obj` for .NET. |

The lower-level repo-confined helpers `walk_repo`, `is_contained`,
`contained_file` and `read_repo_text` are exported too.

## Testing your plugin

- Install the plugin and core into one environment and check it's listed by
  `attackmap modules`.
- Run `attackmap analyze <fixture-repo> -m <name> --strict-analyzers` so any
  exception fails the run.
- In unit tests, `attackmap.analyzers.analyze_repository(root, analyzers=[MyAnalyzer()], strict=True)`
  runs your analyzer through the real merge and provenance path.

`attackmap.analyzers` is internal and may change between minor releases, so
keep such tests close to your pinned core version. The official plugins
(e.g. `attackmap-analyzer-python`, `attackmap-analyzer-go`) are working
templates.

## Conventions

- **Precision over recall.** Validate every heuristic against real
  repositories before release. False positives erode trust fastest. Hold
  speculative signals for `recall`.
- **Exclude noise.** Skip tests and vendored or minified code:
  `include_tests=False` and `DEFAULT_SKIP_DIRS` cover the common cases.
- **Cite evidence.** Emit `file` (repo-relative, via `rel`) and `line` on every
  signal so findings can be diffed and grounded.
- **Never raise for one bad file.** `read_source` returns `None` instead;
  skip the file and, if it matters, add a `limitations` entry.
