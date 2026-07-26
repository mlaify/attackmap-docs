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
which builds the site with `mkdocs build --strict` and rsyncs `./site/` to the
InterServer docroot for `docs.matthewd.xyz`.

Pull requests run the build only — no secrets, no server access — so a broken
internal link fails the PR instead of shipping a 404.

This repo previously published to GitHub Pages via `mkdocs gh-deploy`. There is
no longer a `gh-pages` branch or a `docs/CNAME` file.

### One-time setup

1. **Repository secrets** — Settings → Secrets and variables → Actions:

   | Secret | Value |
   |---|---|
   | `DEPLOY_SSH_KEY` | Private half of an SSH keypair authorized on the InterServer account |
   | `DEPLOY_KNOWN_HOSTS` | Output of `ssh-keyscan -H <host>` — pins the host key |
   | `DEPLOY_HOST` | InterServer hostname or IP |
   | `DEPLOY_USER` | SSH user |
   | `DEPLOY_PATH` | Absolute docroot path for `docs.matthewd.xyz` |
   | `DEPLOY_PORT` | SSH port (optional, defaults to `22`) |

2. **Environment** — create a `production` environment, or remove the
   `environment: production` line from the deploy job.
3. **DNS** — `docs.matthewd.xyz` A record → the InterServer IP, at Cloudflare.
4. **TLS** — install a Cloudflare Origin CA certificate on the server and set
   the SSL mode to Full (strict). Do not use Flexible.
5. **GitHub Pages** — set the source to None so it stops serving the old
   `gh-pages` content and releases the custom-domain claim.

> `DEPLOY_PATH` must point at the `docs.matthewd.xyz` docroot, not the apex
> site's. The deploy uses `rsync --delete`, so a wrong path deletes whatever
> lives there. Dry-run first with `rsync -n`.

## Dependencies

`requirements.txt` is pinned deliberately. MkDocs 2.0 removes the plugin system
and the theming system with no migration path, so an unpinned range would
eventually break this build without a code change here. Bump the pins on
purpose.

## Content

Pages live in [`docs/`](docs/); navigation is defined in
[`mkdocs.yml`](mkdocs.yml). Docs describe the shipped CLI/GUI behavior — when a
feature changes in the engine, update the matching page here.
