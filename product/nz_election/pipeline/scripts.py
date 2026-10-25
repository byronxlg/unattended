"""Filename allowlist: only reviewed local ES modules under PREFIX.

Script tags must have exactly type="module" and a same-origin PREFIX src, with
no inline content or other scripts. Module bytes are not hashed here: build.py
copies or bundles product/nz_election/web/*.mjs from the PR-reviewed code checkout.
"""
from html.parser import HTMLParser

PREFIX = '/unattended/nz-election/'
SCRIPT_ALLOWLIST = {'allocator.mjs', 'electorates.mjs', 'night.mjs', 'night-live.mjs', 'home-live.mjs'}


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


def home_client(web):
    """Inline the shared scheduler so home transfers exactly one reviewed module."""
    scheduler, marker, _ = (web / 'night-live.mjs').read_text().partition("\nif (typeof document")
    client = (web / 'home-live.mjs').read_text()
    dependency = "import {NightLive, OPEN} from './night-live.mjs';\n"
    if not marker or not client.startswith(dependency):
        raise ValueError('HOME_CLIENT_BUNDLE')
    return scheduler + '\n' + client.removeprefix(dependency)
