# Install

AttackMap needs **Python 3.11+**. Pick whichever fits your setup.

=== "Homebrew"

    ```bash
    brew install mlaify/tap/attackmap
    ```

=== "pipx"

    ```bash
    pipx install attackmap
    ```

=== "pip"

    ```bash
    pip install attackmap
    ```

=== "Docker"

    ```bash
    docker run --rm -v "$PWD:/repo" ghcr.io/mlaify/attackmap:latest analyze /repo
    ```

## Optional: LLM support

The AI-review modes work through the `claude` / `codex` CLIs with no extra
install. To use the **API backends** instead, add the LLM extra (pulls in the
`anthropic` and `openai` SDKs):

```bash
pip install "attackmap[llm]"
```

See [AI review](llm.md) for how backends and credentials resolve.

## Optional: everything

The `all` extra adds every official ecosystem analyzer plugin up front (they
also auto-install on demand — see [Analyzers](analyzers.md)):

```bash
pip install "attackmap[all]"
```

## macOS app

Prefer a GUI? Install the native macOS front-end (it drives the same CLI):

```bash
brew install --cask mlaify/tap/attackmap-app   # installs the CLI too
```

See [macOS app](gui.md).

## Verify

```bash
attackmap --help
attackmap modules        # list installed analyzer modules
```
