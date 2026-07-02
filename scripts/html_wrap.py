#!/usr/bin/env python3
"""
html-wrap — Convert an HTML snippet into a standalone, styled HTML document.

Usage:
    python html_wrap.py < input.html > output.html
    python html_wrap.py --title "My PR Review" --style github snippet.html -o review.html
    python html_wrap.py --serve snippet.html          # preview in browser
    echo "<h1>Hello</h1>" | python html-wrap.py -     # read from stdin

As a module:
    from html_wrap import wrap_snippet
    doc = wrap_snippet("<h1>Hi</h1>", title="Review")
    with open("out.html", "w") as f: f.write(doc)
"""

from __future__ import annotations

import argparse
import html
import http.server
import os
import pathlib
import socketserver
import sys
import tempfile
import webbrowser

TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
{style_block}\
</head>
<body>
{content}
</body>
</html>
"""

DEFAULT_STYLE = """
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body {
      font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
      background: #f8f9fb;
      color: #1a1d23;
      line-height: 1.6;
      padding: 2rem 1.5rem;
      max-width: 960px;
      margin: 0 auto;
    }
    pre {
      background: #1e2129;
      color: #e4e7ec;
      padding: 0.6rem 1rem;
      border-radius: 6px;
      overflow-x: auto;
      font-size: 0.85rem;
      line-height: 1.45;
    }
    code { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace; }
    p code, li code { background: #eff1f5; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.85em; }
    kbd {
      display: inline-block; padding: 0.15rem 0.5rem; font-size: 0.8em;
      font-family: 'JetBrains Mono', monospace; background: #eff1f5;
      border: 1px solid #d0d4dc; border-radius: 4px; box-shadow: 0 1px 0 #c4c8d0;
    }
    var { font-style: normal; font-weight: 600; color: #2563eb; }
    details {
      background: #fff; border: 1px solid #e2e5ea; border-radius: 8px;
      margin-bottom: 0.75rem; overflow: hidden;
    }
    details summary {
      cursor: pointer; padding: 0.85rem 1.1rem; font-weight: 600; font-size: 0.9rem;
      background: #fafbfc; border-bottom: 1px solid #e2e5ea; transition: background 0.15s;
    }
    details summary:hover { background: #f0f2f5; }
    details[open] summary { border-bottom-color: #e2e5ea; }
    details > ul, details > ol { padding: 0.75rem 1.25rem 0.75rem 2rem; margin: 0; font-size: 0.9rem; }
    details > ul li, details > ol li { margin-bottom: 0.35rem; }
    .badge {
      display: inline-block; padding: 3px 12px; border-radius: 20px;
      font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.04em; color: #fff;
    }
    .badge-warning { background: #f59e0b; }
    .badge-success { background: #16a34a; }
    .badge-danger  { background: #dc2626; }
    .badge-info    { background: #2563eb; }
    .badge-neutral { background: #6b7280; }
    table.impact {
      width: 100%; border-collapse: collapse; font-size: 0.88rem;
      background: #fff; border-radius: 8px; overflow: hidden;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    table.impact th {
      background: #f4f5f7; padding: 10px 14px; text-align: left;
      font-weight: 600; border-bottom: 2px solid #dce0e6;
    }
    table.impact td { padding: 10px 14px; border-bottom: 1px solid #edf0f4; vertical-align: top; }
    table.impact tr:last-child td { border-bottom: none; }
    aside.warn {
      margin: 1.75rem 0; padding: 1.1rem 1.25rem;
      border-left: 4px solid #f59e0b; background: #fffbeb; border-radius: 8px; font-size: 0.9rem;
    }
    aside.warn h4 { margin: 0 0 0.5rem; color: #92400e; }
    aside.warn ul { margin: 0; padding-left: 1.25rem; }
    aside.warn ul li { margin-bottom: 0.35rem; }
    @media print {
      body { color: #000; background: #fff; }
      details { border: 1px solid #ccc; break-inside: avoid; }
      details summary { background: #f5f5f5; border-bottom: 1px solid #ccc; }
      details[open] { break-inside: avoid; }
      .badge { border: 1px solid #666; color: #000 !important; background: #eee !important; }
      kbd { border-color: #999; box-shadow: none; }
      pre { background: #f5f5f5; color: #000; border: 1px solid #ccc; }
      aside.warn { border-left-color: #f59e0b; background: #fffbe6; }
      aside.warn h4 { color: #92400e; }
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
    }
    @media (prefers-color-scheme: dark) {
      body { background: #12141a; color: #e4e7ec; }
      details { background: #1a1d26; border-color: #2c2f3a; }
      details summary { background: #1e2129; border-bottom-color: #2c2f3a; color: #e4e7ec; }
      details summary:hover { background: #252833; }
      p code, li code { background: #252833; }
      kbd { background: #252833; border-color: #3a3e4a; box-shadow: 0 1px 0 #3a3e4a; }
      table.impact { background: #1a1d26; }
      table.impact th { background: #1e2129; border-bottom-color: #2c2f3a; }
      table.impact td { border-bottom-color: #2c2f3a; }
      aside.warn { background: #2a2416; border-left-color: #f59e0b; }
      aside.warn h4 { color: #fbbf24; }
      .badge-warning { background: #d97706; }
    }
  </style>"""


def read_source(source: str | None) -> str:
    """Read snippet from a file path (or '-' for stdin)."""
    if source is None or source == "-":
        return sys.stdin.read()
    try:
        return pathlib.Path(source).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: file not found: {source}", file=sys.stderr)
        sys.exit(1)


def wrap_snippet(
    content: str,
    title: str = "Document",
    style: str | None = None,
    minify: bool = False,
) -> str:
    """Wrap an HTML snippet into a complete HTML document.

    Args:
        content:    The HTML snippet (no <html>/<body> tags needed).
        title:      Value for <title>.
        style:      Inline <style> block. Pass None for the built-in default.
        minify:     Remove blank lines around the content boundary.

    Returns:
        A complete HTML document string.
    """
    style_block = style if style is not None else DEFAULT_STYLE
    if minify:
        content = content.strip()
    return TEMPLATE.format(title=html.escape(title), style_block=style_block, content=content)


def serve_document(doc: str, port: int = 0, no_open: bool = False) -> None:
    """Serve the HTML string on a temporary local server and open the browser."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(doc)
        tmp = f.name

    class _Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=os.path.dirname(tmp), **kw)

        def log_message(self, fmt, *args):
            pass  # quieter

    with socketserver.TCPServer(("127.0.0.1", port or 0), _Handler) as httpd:
        host, port = httpd.server_address
        url = f"http://{host}:{port}/{os.path.basename(tmp)}"
        print(f"  Serving at {url}", file=sys.stderr)
        if not no_open:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Shutting down.", file=sys.stderr)
        finally:
            pathlib.Path(tmp).unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert an HTML snippet into a standalone HTML document.",
    )
    parser.add_argument(
        "source",
        nargs="?",
        default="-",
        metavar="FILE",
        help="Path to snippet file (or '-' for stdin). Default: stdin.",
    )
    parser.add_argument("-o", "--output", metavar="FILE", help="Write to file instead of stdout.")
    parser.add_argument("-t", "--title", default="Document", help="Document <title>.")
    parser.add_argument(
        "--style",
        metavar="FILE",
        help="Path to a custom CSS/<style> file to inject instead of the default.",
    )
    parser.add_argument(
        "--append-style",
        metavar="FILE",
        help="Path to a CSS/<style> file to append after the default (or custom --style) stylesheet.",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open browser when used with --serve.",
    )
    parser.add_argument(
        "--minify",
        action="store_true",
        help="Strip leading/trailing whitespace from content (not full HTML minification).",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Preview in browser on a temporary HTTP server.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Port for --serve (default: random available port).",
    )

    args = parser.parse_args()
    content = read_source(args.source)

    custom_style = None
    if args.style:
        custom_style = "<style>\n" + pathlib.Path(args.style).read_text(encoding="utf-8") + "\n</style>"
    if args.append_style:
        append = "<style>\n" + pathlib.Path(args.append_style).read_text(encoding="utf-8") + "\n</style>"
        base = custom_style if custom_style is not None else DEFAULT_STYLE
        custom_style = base.rstrip() + "\n" + append

    doc = wrap_snippet(
        content,
        title=args.title,
        style=custom_style,
        minify=args.minify,
    )

    if args.serve:
        serve_document(doc, port=args.port, no_open=args.no_open)
    elif args.output:
        pathlib.Path(args.output).write_text(doc, encoding="utf-8")
        print(f"Wrote {len(doc):,} bytes to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(doc)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
