# Install

AttackMap needs **Python 3.11+**. Pick whichever fits your setup.

=== "pipx"

    ```bash
    pipx install git+https://github.com/mlaify/AttackMap.git
    ```

=== "pip"

    ```bash
    pip install git+https://github.com/mlaify/AttackMap.git
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
pip install "git+https://github.com/mlaify/AttackMap.git#egg=attackmap[llm]"
```

See [AI review](llm.md) for how backends and credentials resolve.

## Optional: everything

The `all` extra adds every official ecosystem analyzer plugin up front (they
also auto-install on demand — see [Analyzers](analyzers.md)):

```bash
pip install "git+https://github.com/mlaify/AttackMap.git#egg=attackmap[all]"
```

## macOS app

Prefer a GUI? Build the native macOS front-end from source (it drives the same
CLI): [mlaify/AttackMap-mac](https://github.com/mlaify/AttackMap-mac).

See [macOS app](gui.md).

## Verify

```bash
attackmap --help
attackmap modules        # list installed analyzer modules
```
