# attackmap-docs

Documentation site for [AttackMap](https://github.com/mlaify/AttackMap), built
with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and served
at **[docs.matthewd.xyz](https://docs.matthewd.xyz)**.

## Local development

```bash
pip install -r requirements.txt
mkdocs serve          # live preview at http://127.0.0.1:8000
mkdocs build          # output to ./site
```

## Deploy

Pushing to `main` runs [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml),
which builds the site and publishes it to the `gh-pages` branch. GitHub Pages
serves that branch; [`docs/CNAME`](docs/CNAME) pins the custom domain.

Pull requests run the build only — `mkdocs build --strict`, with no write
permissions — so a broken internal link fails the PR instead of shipping a 404.

### One-time setup

1. **Pages source** — Settings → Pages → Deploy from branch → `gh-pages` / `root`.
2. **DNS** — add a `CNAME` record at your DNS provider:
   `docs.matthewd.xyz` → `mlaify.github.io`.
3. **Custom domain** — Settings → Pages → set `docs.matthewd.xyz`; enable
   "Enforce HTTPS" once the certificate provisions.

## Dependencies

`requirements.txt` is pinned deliberately. MkDocs 2.0 removes the plugin system
and the theming system with no migration path, so an unpinned range would
eventually break this build without a code change here. Bump the pins on
purpose.

## Content

Pages live in [`docs/`](docs/); navigation is defined in
[`mkdocs.yml`](mkdocs.yml). Docs describe the shipped CLI/GUI behavior — when a
feature changes in the engine, update the matching page here.
