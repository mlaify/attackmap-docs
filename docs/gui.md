# macOS app

A native SwiftUI front-end that drives the `attackmap` CLI and renders its
results — pick a repo, run a scan, and browse findings, exploitability, attack
paths, diagrams, and the AI review without leaving the app.

## Install

```bash
brew install --cask mlaify/tap/attackmap-app
```

The cask depends on the `attackmap` formula, so this installs the CLI too. Update
both together:

```bash
brew upgrade --cask attackmap-app
```

Requires macOS 15 (Sequoia) or later.

## Features

- **Repo picker + Run/Cancel** with live progress and ETA.
- **Analyzers** — Automatic (by language) or pin specific modules.
- **AI review** — provider (Claude / OpenAI · Codex), model, reasoning, and Fast toggle. API keys are stored in your login Keychain.
- **Watch mode** — auto re-scan on file changes, with new-vs-resolved deltas.
- **Result views** — Overview, Findings, Exploitability, Attack paths, Attack surface, Diagrams (rendered Mermaid), Review, and AI Review.

The app feature-detects the installed CLI, so newer options light up as you
upgrade. Source and issues: [github.com/mlaify/AttackMap-mac](https://github.com/mlaify/AttackMap-mac).
