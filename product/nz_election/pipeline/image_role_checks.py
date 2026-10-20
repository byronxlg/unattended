"""Reject focusable descendants hidden by an image's atomic accessibility role."""
from html.parser import HTMLParser


class ImageRoles(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.stack = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        focusable = ('tabindex' in attrs
                     or tag in {'a', 'area'} and ('href' in attrs or 'xlink:href' in attrs)
                     or tag in {'button', 'select', 'textarea', 'summary', 'iframe'}
                     or tag == 'input' and attrs.get('type') != 'hidden'
                     or tag in {'audio', 'video'} and 'controls' in attrs
                     or 'contenteditable' in attrs and attrs['contenteditable'] != 'false')
        if focusable and any(role == 'img' for _, role in self.stack):
            raise ValueError(f'ROLE_IMG_FOCUS: focusable <{tag}> inside role="img"')
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append((tag, attrs.get('role')))

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)


def check_page(html):
    ImageRoles(html)
