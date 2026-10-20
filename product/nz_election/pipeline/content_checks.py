"""Semantic absence and provenance checks for static HTML."""
from html.parser import HTMLParser

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    @property
    def text(self):
        return ''.join(c if isinstance(c, str) else c.text for c in self.children)


class Tree(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.root = Node()
        self.stack, self.nodes = [self.root], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        self.nodes.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def check_sources(html):
    tree = Tree(html)
    ids = {n.attrs['id']: n for n in tree.nodes if 'id' in n.attrs}
    for node in tree.nodes:
        refs = node.attrs.get('aria-describedby', '').split()
        href = node.attrs.get('href', '')
        if href.startswith('#source-'):
            refs.append(href[1:])
        for ref in refs:
            if ref.startswith('source-'):
                target = ids.get(ref)
                if target is None or not target.text.strip():
                    raise ValueError('EMPTY_PROVENANCE: ' + ref)


def check_empty_headings(html):
    tree = Tree(html)
    for parent in tree.nodes:
        children = parent.children
        for i, node in enumerate(children):
            if not isinstance(node, Node) or node.tag not in {'h2', 'h3', 'h4'}:
                continue
            following = []
            for sibling in children[i+1:]:
                if isinstance(sibling, Node) and sibling.tag in {'h1', 'h2', 'h3', 'h4'}:
                    break
                following.append(sibling)
            # A heading introduces content in its own container, not a later module.
            meaningful = [c for c in following if (c.strip() if isinstance(c, str)
                          else c.tag not in {'script', 'style'} and
                          'source-note' not in c.attrs.get('class', '').split() and
                          (c.text.strip() or c.tag in {'svg', 'img', 'canvas', 'input'}))]
            if not meaningful:
                raise ValueError('EMPTY_MODULE: ' + node.text.strip())
