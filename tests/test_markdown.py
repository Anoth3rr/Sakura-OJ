from app.markdown import render_markdown


def test_markdown_renders_common_problem_statement_features_safely():
    rendered = render_markdown(
        "# 题目\n\n| 输入 | 输出 |\n| --- | --- |\n| 1 | 2 |\n\n[危险链接](javascript:alert(1))"
    )
    assert "<h1>" in rendered
    assert "<table>" in rendered
    assert 'href="javascript:' not in rendered


def test_markdown_renders_inline_and_centered_latex_without_touching_code():
    rendered = render_markdown(
        "行内 $$a^2+b^2$$。\n\n$$$$\n\\sum_{i=1}^{n} i\n$$$$\n\n```text\n$$literal$$\n```"
    )
    assert '<span class="math-inline">\\(a^2+b^2\\)</span>' in rendered
    assert '<span class="math-display">\\[\\sum_{i=1}^{n} i\\]</span>' in rendered
    assert "$$literal$$" in rendered


def test_markdown_keeps_legacy_single_dollar_formulas_compatible():
    rendered = render_markdown("选择 $s$，价格 $5，代码 ` $x$ `。")
    assert '<span class="math-inline">\\(s\\)</span>' in rendered
    assert "$5" in rendered
    assert "$x$" in rendered


def test_markdown_accepts_escaped_dollar_inside_formula():
    rendered = render_markdown(r"金额 $$\$5 + \$2$$")
    assert '<span class="math-inline">\\(\\$5 + \\$2\\)</span>' in rendered


def test_labeled_samples_preserve_text_whitespace_and_pair_metadata():
    rendered = render_markdown(
        "## 样例\n\n```text input:#2\n  <$x$>\n\n```\n\n"
        "```text output:#2\n& 42\n```\n\n```cpp\ncout << 42;\n```"
    )
    assert 'data-sample-kind="input" data-sample-number="2"' in rendered
    assert 'data-sample-kind="output" data-sample-number="2"' in rendered
    assert "  &lt;$x$&gt;\n\n</code>" in rendered
    assert "&amp; 42\n</code>" in rendered
    assert rendered.count("data-sample-kind") == 2
    assert "math-inline" not in rendered


def test_invalid_sample_label_cannot_create_metadata_or_html():
    rendered = render_markdown('```text input:#1" onclick="alert(1)\n<script>alert(1)</script>\n```')
    assert "data-sample-kind" not in rendered
    assert 'onclick="' not in rendered
    assert "<script>" not in rendered
