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

Cloudflare **Workers Builds** clones this repo on push, runs the build itself,
and deploys the result as Workers static assets. There is no GitHub Actions
workflow, no SSH key, no rsync, and no origin server.

| | |
|---|---|
| Worker | `docs-matthewd-xyz` |
| Config | [`wrangler.jsonc`](wrangler.jsonc) |
| Production branch | `main` → `https://docs.matthewd.xyz` |
| Any other branch | preview URL, not promoted to production |

This repo previously published to GitHub Pages via `mkdocs gh-deploy`, then to an
InterServer docroot by rsync. There is no `gh-pages` branch and no `docs/CNAME`.

### Build settings (Cloudflare dashboard)

Workers & Pages → `docs-matthewd-xyz` → Settings → Build:

| Setting | Value |
|---|---|
| Build command | `npm run build:cf` |
| Deploy command | `npx wrangler deploy` |
| Non-production deploy command | `npx wrangler versions upload` |
| Root directory | *(blank)* |

`build:cf` lives in [`package.json`](package.json) so the actual steps stay in
version control and the dashboard holds only the entry point. It installs the
pinned requirements, runs `mkdocs build --strict`, deletes source maps, then runs
[`scripts/check-build.sh`](scripts/check-build.sh).

mkdocs-material ships ~1.3 MB of source maps for its own bundled CSS/JS. These
are not published; `build:cf` deletes them and `check-build.sh` fails the build
if any survive. A Cloudflare `.assetsignore` cannot do this — it has to sit in
the assets directory root (`site/`), and MkDocs does not copy dotfiles from
`docs/`.

`--strict` still turns a broken internal link or bad nav reference into a build
failure, and a failed build never becomes a deployment — so a typo cannot ship a
404. That guarantee now applies to preview branches too.

### Toolchain pinning

| Tool | Pinned to | Where |
|---|---|---|
| Python | 3.12 | [`.python-version`](.python-version) |
| MkDocs + Material | see below | [`requirements.txt`](requirements.txt) |
| wrangler | 4.114.0 | `devDependencies` in `package.json` |

Node exists in this repo **only** to pin wrangler; the site is built by MkDocs.
Without `.python-version` the build image would use its default (3.13.x).

`build:cf` installs into a `.venv` rather than the system interpreter. Python
3.12+ images mark that externally managed (PEP 668) and a bare
`pip install -r requirements.txt` fails there.

### Headers

[`docs/_headers`](docs/_headers) is the single source of truth for security and
cache headers. MkDocs copies it to `site/_headers`, Cloudflare consumes it at
deploy time, and it is not itself served.

This used to come from the origin (LiteSpeed/cPanel). There is no origin now, so
if a Cloudflare Transform Rule also sets these headers, remove one side —
duplicated security headers are worse than none.

### Local preview through the real asset router

```bash
npm run build:cf && npm run preview
```

`preview` runs `wrangler dev`, which serves `site/` through the same asset router
as production — trailing-slash behaviour, the 404 page, and `_headers` all apply.
`mkdocs serve` reproduces none of those.

Cutover steps, the DNS swap ordering constraint, and rollback are in the sibling
repo's runbook:
`mlaify/mlaify.github.io` → `docs/superpowers/ops/cloudflare-workers-runbook.md`.
It covers both sites.

## Dependencies

`requirements.txt` is pinned deliberately. MkDocs 2.0 removes the plugin system
and the theming system with no migration path, so an unpinned range would
eventually break this build without a code change here. Bump the pins on
purpose.

## Content

Pages live in [`docs/`](docs/); navigation is defined in
[`mkdocs.yml`](mkdocs.yml). Docs describe the shipped CLI/GUI behavior — when a
feature changes in the engine, update the matching page here.
