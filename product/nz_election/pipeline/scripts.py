"""The only executable page assets are reviewed local ES modules."""
from html.parser import HTMLParser

PREFIX = '/unattended/nz-election/'
SCRIPT_ALLOWLIST = {'coalitions.mjs', 'allocator.mjs'}


def validate_scripts(html):
    class Scripts(HTMLParser):
        active = False

        def handle_starttag(self, tag, attrs):
            if tag != 'script':
                return
            if (self.active or len(attrs) != 2 or dict(attrs).get('type') != 'module'
                    or dict(attrs).get('src') not in {PREFIX + p for p in SCRIPT_ALLOWLIST}):
                raise ValueError('UNSAFE_SCRIPT')
            self.active = True

        def handle_data(self, data):
            if self.active and data:
                raise ValueError('UNSAFE_SCRIPT')

        def handle_endtag(self, tag):
            if tag == 'script':
                if not self.active:
                    raise ValueError('UNSAFE_SCRIPT')
                self.active = False

    parser = Scripts()
    parser.feed(html)
    parser.close()
    if parser.active:
        raise ValueError('UNSAFE_SCRIPT')
    return True
