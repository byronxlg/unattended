"""Keep server-rendered content visible without disclosure controls."""
import re


def open_prose(html):
    # Expand the innermost disclosure first so nested metadata cannot stay hidden.
    pattern = r'<details(?P<attrs>\s[^>]*)?>(?P<body>(?:(?!<details).)*?)</details>'
    while re.search(pattern, html, re.S):
        def expand(match):
            body = re.sub(r'<summary>(.*?)</summary>', r'<p class="disclosure-label">\1</p>', match['body'], flags=re.S)
            attrs = re.sub(r'\sopen(?:="[^"]*")?', '', match['attrs'] or '')
            return '<div' + attrs + '>' + body + '</div>'
        html = re.sub(pattern, expand, html, flags=re.S)
    return html
