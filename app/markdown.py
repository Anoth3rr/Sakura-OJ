from __future__ import annotations

from html import escape
import re

import bleach
from markdown_it import MarkdownIt


_MARKDOWN = MarkdownIt("commonmark", {"html": False, "breaks": True}).enable(
    ("table", "strikethrough")
)
_ALLOWED_TAGS = {
    "a",
    "blockquote",
    "br",
    "code",
    "del",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "s",
    "span",
    "div",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "ul",
}
_ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "code": ["class", "data-sample-kind", "data-sample-number"],
    "span": ["class"],
    "div": ["class"],
}

_BLOCK_MATH = re.compile(r"(?<![$\\])\${4}(?P<body>[\s\S]+?)(?<![$\\])\${4}")
_INLINE_MATH = re.compile(
    r"(?<![$\\])\${2}(?P<body>(?:\\.|[^$\r\n])+?)(?<![$\\])\${2}"
)
_LEGACY_INLINE_MATH = re.compile(
    r"(?<![$\\])\$(?!\$)(?P<body>(?:\\.|[^$\\\r\n])+?)(?<!\\)\$(?!\$)"
)
_MATH_MARKER = "SAKURAMATH{}TOKEN"
_CODE_MARKER = "SAKURACODE{}TOKEN"


def _protect_code(source: str) -> tuple[str, list[str]]:
    """Keep fenced and inline code opaque while math delimiters are parsed."""

    protected: list[str] = []

    def save(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return _CODE_MARKER.format(len(protected) - 1)

    # Fences are handled first so backticks inside a code block are untouched.
    source = re.sub(r"(?ms)^[ \t]{0,3}(\`{3,}|~{3,})[^\n]*\n.*?^[ \t]{0,3}\1[ \t]*$", save, source)
    source = re.sub(r"(?m)^(?: {4}|\t).*(?:\n(?: {4}|\t).*)*", save, source)
    source = re.sub(r"(?s)(\`+)(.+?)\1", save, source)
    return source, protected


def _restore_code(source: str, protected: list[str]) -> str:
    for index, value in enumerate(protected):
        source = source.replace(_CODE_MARKER.format(index), value)
    return source


def _replace_math_tokens(value: str, formulas: list[tuple[bool, str]]) -> str:
    """Replace supported delimiters with inert ASCII markers before Markdown rendering."""

    def block_replacer(match: re.Match[str]) -> str:
        body = match.group("body")
        if not body.strip():
            return match.group(0)
        index = len(formulas)
        formulas.append((True, body.strip()))
        return _MATH_MARKER.format(index)

    value = _BLOCK_MATH.sub(block_replacer, value)

    def inline_replacer(match: re.Match[str]) -> str:
        body = match.group("body")
        if not body.strip():
            return match.group(0)
        index = len(formulas)
        formulas.append((False, body.strip()))
        return _MATH_MARKER.format(index)

    value = _INLINE_MATH.sub(inline_replacer, value)
    # 旧题面使用单美元行内公式；保留兼容性，同时不触碰代码片段。
    return _LEGACY_INLINE_MATH.sub(inline_replacer, value)


def _render_math(formula: str, *, display: bool) -> str:
    # Formula content is escaped before inserting generated HTML. KaTeX then
    # consumes the \(...\) / \[...\] delimiters in the browser.
    escaped = escape(formula, quote=False)
    if display:
        return f'<span class="math-display">\\[{escaped}\\]</span>'
    return f'<span class="math-inline">\\({escaped}\\)</span>'


def _render_with_math(source: str) -> str:
    formulas: list[tuple[bool, str]] = []
    source, protected = _protect_code(source or "")
    source = _replace_math_tokens(source, formulas)
    source = _restore_code(source, protected)
    tokens = _MARKDOWN.parse(source)
    # Preserve explicit sample labels for the OJ's paired input/output display.
    # The standard fence renderer still escapes the sample content as plain text.
    for token in tokens:
        if token.type == "fence":
            sample = re.fullmatch(r"text\s+(input|output):#([1-9][0-9]*)", token.info.strip())
            if sample:
                token.attrSet("data-sample-kind", sample[1])
                token.attrSet("data-sample-number", sample[2])

    rendered = _MARKDOWN.renderer.render(tokens, _MARKDOWN.options, {})
    rendered = bleach.clean(
        rendered,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        protocols={"http", "https", "mailto"},
        strip=True,
    )
    for index, (display, formula) in enumerate(formulas):
        marker = _MATH_MARKER.format(index)
        math_html = _render_math(formula, display=display)
        if display:
            # A standalone four-dollar expression is a full-width block. The
            # fallback replacement still renders correctly when text surrounds it.
            rendered = re.sub(
                rf"<p>\s*{re.escape(marker)}\s*</p>",
                lambda _: math_html,
                rendered,
                count=1,
            )
        rendered = rendered.replace(marker, math_html)
    return rendered


def render_markdown(source: str) -> str:
    """Render safe Markdown with $$ inline, $$$$ centered, and legacy $ formulas."""
    return _render_with_math(source)
