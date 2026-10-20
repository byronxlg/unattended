"""Check all route landmarks including the actual coalition startup output, without Chromium."""
from collections import Counter
import json
from pathlib import Path
import subprocess

from product.nz_election.tests.design_checks import Document, provenance


def rendered_page(site, html):
    nodes = Document(html).nodes
    explorer = next((attrs for _, attrs in nodes if attrs.get('id') == 'coalition-explorer'), {})
    if not explorer.get('data-averages'):
        return html
    parties = [dict(partyRow=a['data-party-row'], name=a['data-name'], colour=a['data-colour'])
               for _, a in nodes if 'data-party-row' in a]
    payload = dict(site=str(site.resolve()), parties=parties,
                   explorer={key.removeprefix('data-'): value for key, value in explorer.items()
                             if key.startswith('data-')})
    script = Path(__file__).resolve().parents[1] / 'tools/render_coalition.mjs'
    result = subprocess.run(['node', str(script)], input=json.dumps(payload), text=True,
                            capture_output=True, check=True, timeout=15)
    marker = '<div data-picture></div>'
    if html.count(marker) != 1:
        raise ValueError('CLIENT_PICTURE_TARGET: expected one explorer output')
    return html.replace(marker, '<div data-picture>' + result.stdout + '</div>')


def check_page(html):
    from product.nz_election.pipeline.image_role_checks import check_page as check_image_roles
    check_image_roles(html)
    from product.nz_election.pipeline.content_checks import check_sources
    check_sources(html)
    provenance(html)
    regions = [a for _, a in Document(html).nodes if a.get('role') == 'region']
    names = Counter(a.get('aria-label') for a in regions)
    duplicates = sorted(name or '(unnamed)' for name, count in names.items() if count > 1)
    if duplicates:
        raise ValueError('DUPLICATE_REGION: ' + ', '.join(duplicates))
    for attrs in regions:
        if 'scroll' in attrs.get('class', '').split():
            if attrs.get('tabindex') != '0' or not attrs.get('aria-label'):
                raise ValueError('SCROLL_REGION: named keyboard target required')


def check_site(site):
    pages = sorted(site.rglob('index.html'))
    if not pages:
        raise ValueError('LANDMARK_CHECK: no pages found')
    for page in pages:
        try:
            check_page(rendered_page(site, page.read_text()))
        except ValueError as exc:
            raise ValueError(f'{page.relative_to(site)}: {exc}') from exc
    return len(pages)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path)
    args = parser.parse_args()
    print(f'PASS landmarks: {check_site(args.site)} routes including client-rendered tables')
