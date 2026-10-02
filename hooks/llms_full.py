"""MkDocs hook: write site/llms-full.txt, the full text of every page in nav order."""
from pathlib import Path


def _nav_files(nav):
    for item in nav or []:
        if isinstance(item, str):
            yield item
        elif isinstance(item, dict):
            for value in item.values():
                yield from _nav_files([value] if isinstance(value, str) else value)


def on_post_build(config, **kwargs):
    docs = Path(config["docs_dir"])
    site_url = config["site_url"].rstrip("/") + "/"
    parts = [
        f"# {config['site_name']} documentation — full text",
        "",
        f"> {' '.join((config.get('site_description') or '').split())}",
        "",
        f"This file contains the text of every page on {site_url}. A shorter index is at {site_url}llms.txt.",
    ]
    for rel in _nav_files(config["nav"]):
        page = rel[:-3]
        url = site_url if page == "index" else f"{site_url}{page.removesuffix('/index')}/"
        parts += ["", "---", "", f"URL: {url}", "", (docs / rel).read_text(encoding="utf-8").strip()]
    Path(config["site_dir"], "llms-full.txt").write_text("\n".join(parts) + "\n", encoding="utf-8")
