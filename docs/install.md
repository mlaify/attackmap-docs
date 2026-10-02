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

## Optional: LLM support

The AI-review modes work through the `claude` / `codex` CLIs with no extra
install. To use the **API backends** instead, add the LLM extra (pulls in the
`anthropic` and `openai` SDKs):

```bash
pip install "attackmap[llm] @ git+https://github.com/mlaify/AttackMap.git"
```

See [AI review](llm.md) for how backends and credentials resolve.

## Optional: everything

The `all` extra adds all 15 official ecosystem analyzer plugins up front,
pinned to the commits in AttackMap's plugin lock. Without it, a plain
`attackmap analyze` never installs plugins; use `attackmap suggest . --install`
or `--module <name>` (see [Analyzers](analyzers.md#installing-plugins)):

```bash
pip install "attackmap[all] @ git+https://github.com/mlaify/AttackMap.git"
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
