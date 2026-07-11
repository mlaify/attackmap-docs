# Analyzer SDK

An analyzer is a small Python package that inspects a repository and returns
structured signals. AttackMap discovers analyzers through a Python **entry
point**, so your plugin is just a package that advertises itself — no changes to
AttackMap core.

!!! info "Canonical contract"
    The authoritative types live in `src/attackmap/sdk/` in the
    [engine repo](https://github.com/mlaify/AttackMap). If this page and the repo
    ever disagree, the repo is correct.

## The contract

An analyzer exposes a `metadata` attribute and an `analyze` method
(`AnalyzerProtocol`):

```python
from pathlib import Path
from attackmap.sdk import AnalyzerMetadata, AnalyzerResult

class MyAnalyzer:
    metadata = AnalyzerMetadata(
        name="my-ecosystem",              # slug; also the --module key
        display_name="My Ecosystem Analyzer",
        description="Detects routes and sinks in <framework>.",
        scope="Repositories using <framework>.",
        languages=["python"],
        targets=["my-framework"],
        enabled_by_default=False,         # broad language analyzers set True
        priority=120,                     # lower runs first
    )

    def analyze(self, root: str | Path) -> AnalyzerResult:
        ...
        return AnalyzerResult(...)
```

`AnalyzerMetadata` is what `attackmap modules` reports and what auto-selection
and `ecosystems` are computed from.

## Register the entry point

Advertise the analyzer under the **`attackmap.analyzers`** group in your
package's `pyproject.toml`:

```toml
[project.entry-points."attackmap.analyzers"]
my-ecosystem = "my_package.analyzer:MyAnalyzer"
```

Once the package is installed in the same environment as AttackMap, it appears
in `attackmap modules` and can be selected with `--module my-ecosystem`.

## What `analyze` returns

`AnalyzerResult` carries the signals AttackMap fuses into the report — routes /
attack surfaces, taint sources and sinks, dependency hints, and findings, each
tagged with provenance so the engine can attribute and cross-reference them.
Start from an existing plugin (e.g. `attackmap-analyzer-python` or
`attackmap-analyzer-go`) as a working template.

## Conventions

- **Precision over recall.** Every heuristic should be validated against real
  repositories before release — false positives erode trust fastest.
- **Exclude noise.** Skip test files and vendored/minified third-party code (the
  SDK provides helpers for this).
- **Cite evidence.** Emit stable, locatable signals (file + line) so findings
  can be diffed and grounded.
