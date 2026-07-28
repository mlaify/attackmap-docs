#!/usr/bin/env bash
#
# Assert that the MkDocs build produced everything the site needs before it is
# deployed.
#
# These checks came from the old GitHub Actions workflow and are kept because
# Workers Builds will happily deploy a technically-successful build that is
# missing its search index. Failing here means the bad build never becomes a
# deployment.
#
# `mkdocs build --strict` already fails on broken internal links and bad nav
# references; this covers what --strict does not assert.

set -euo pipefail

fail=0
note() {
	printf '  %s\n' "$1"
	fail=1
}

[ -f site/index.html ] || note "site/index.html missing"
[ -f site/404.html ] || note "site/404.html missing — not_found_handling: 404-page has nothing to serve"
[ -d site/search ] || note "site/search missing — search index not built"

# Cloudflare reads site/_headers at deploy time and does not serve it. If it is
# absent the deploy still succeeds, silently dropping every security header and
# cache rule — the whole site's header policy lives in this one file, so check
# it explicitly.
[ -f site/_headers ] || note "site/_headers missing — docs/_headers did not reach the build output"

# mkdocs-material ships ~1.3 MB of source maps for its own bundled CSS/JS.
# `build:cf` deletes them; this asserts the deletion actually happened, because
# nothing else would notice them being published.
#
# Note this cannot be done with a Cloudflare .assetsignore file: that has to sit
# in the assets directory root (site/), and MkDocs does not copy dotfiles from
# docs/ into site/ — verified. Deleting them post-build is the working approach.
maps=$(find site -name '*.map' | wc -l | tr -d ' ')
[ "$maps" = "0" ] || note "$maps source map(s) still in site/ — the find -delete in build:cf did not run"

if [ "$fail" -ne 0 ]; then
	printf 'Build output is not deployable.\n' >&2
	exit 1
fi

printf 'Build output looks sane (%s files).\n' "$(find site -type f | wc -l | tr -d ' ')"
