"""Check all route landmarks in server-rendered output, without Chromium."""
from collections import Counter
from pathlib import Path

from product.nz_election.tests.design_checks import Document, provenance


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
            check_page(page.read_text())
        except ValueError as exc:
            raise ValueError(f'{page.relative_to(site)}: {exc}') from exc
    return len(pages)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path)
    args = parser.parse_args()
    print(f'PASS landmarks: {check_site(args.site)} routes including server-rendered tables')
