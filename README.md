# attackmap-docs

Documentation site for [AttackMap](https://github.com/mlaify/AttackMap), built
with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and served
at **[docs.fhrp.org](https://docs.fhrp.org)**.

## Local development

```bash
pip install -r requirements.txt
mkdocs serve          # live preview at http://127.0.0.1:8000
mkdocs build          # output to ./site
```

## Deploy

Pushing to `main` runs [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml),
which builds the site with `mkdocs build --strict` and rsyncs `./site/` to the
InterServer docroot for `docs.fhrp.org`.

This repo previously published to GitHub Pages via `mkdocs gh-deploy`. That was
replaced when the site moved to InterServer; there is no longer a `gh-pages`
branch or a `docs/CNAME` file.

### One-time setup

1. **Repository secrets** — Settings → Secrets and variables → Actions:

   | Secret | Value |
   |---|---|
   | `DEPLOY_SSH_KEY` | Private half of an SSH keypair authorized on the InterServer account |
   | `DEPLOY_KNOWN_HOSTS` | Output of `ssh-keyscan -H <host>` — pins the host key |
   | `DEPLOY_HOST` | InterServer hostname or IP |
   | `DEPLOY_USER` | SSH user |
   | `DEPLOY_PATH` | Absolute docroot path for `docs.fhrp.org` |
   | `DEPLOY_PORT` | SSH port (optional, defaults to `22`) |

2. **DNS** — `docs.fhrp.org` A record → the InterServer IP, at Cloudflare.
3. **TLS** — issue a certificate for `docs.fhrp.org` on the server, or set the
   Cloudflare SSL mode to Full (strict) with an origin certificate installed.

## Content

Pages live in [`docs/`](docs/); navigation is defined in
[`mkdocs.yml`](mkdocs.yml). Docs describe the shipped CLI/GUI behavior — when a
feature changes in the engine, update the matching page here.
