"""Check local references and file-name case for the complete static portfolio."""
from collections import Counter
from html.parser import HTMLParser
import posixpath
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids, self.refs = [], []
        self.feed(path.read_text(encoding="utf-8-sig"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("src", "href"):
            if attrs.get(key):
                self.refs.append(attrs[key])
        if attrs.get("property") == "og:image":
            self.refs.append(attrs["content"])


def main():
    files = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*")
             if p.is_file() and ".git" not in p.relative_to(ROOT).parts}
    pages = {f: Page(ROOT / f) for f in sorted(files) if f.endswith(".html")}
    errors = []
    for filename, page in pages.items():
        for key, count in Counter(page.ids).items():
            if count > 1:
                errors.append(f"Duplicate id in {filename}: {key}")
        for ref in page.refs:
            url = urlsplit(ref)
            if (url.scheme or url.netloc) and url.hostname != "etherealbian.github.io":
                continue
            path = unquote(url.path)
            if not path:
                target = filename
            else:
                if path.endswith("/"):
                    path += "index.html"
                target = posixpath.normpath(posixpath.join(posixpath.dirname(filename), path)).lstrip("/")
            if target not in files:
                errors.append(f"{filename}: missing file or incorrect case: {ref}")
            elif target in pages and url.fragment and unquote(url.fragment) not in pages[target].ids:
                errors.append(f"{filename}: target has no such anchor: {ref}")
    for name in sorted(files):
        if name.endswith(".svg"):
            try:
                ElementTree.parse(ROOT / name)
            except ElementTree.ParseError as exc:
                errors.append(f"{name}: {exc}")
    if ".nojekyll" not in files:
        errors.append("Missing GitHub Pages .nojekyll marker")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK: {len(pages)} pages; anchors, relative paths, filename case, SVGs and Pages marker.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
