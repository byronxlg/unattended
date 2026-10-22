"""Offline upstream default rotation and strict model validation regressions."""
import json

import pytest

from product.nz_election.pipeline import export, social
from product.nz_election.tests.test_social import DAY, NOW, post, response


def test_reserved_refresh_survives_upstream_default_rotation(tmp_path):
    out = tmp_path / 'data'
    reservation = social.refresh_social(out, DAY, now=NOW, reserve=True)
    upstream = social.fixture_send()
    requested = []

    def send(method, url, headers, payload):
        status, raw = upstream(method, url, headers, payload)
        if method == 'POST':
            model = json.loads(payload)['model']
            requested.append(model)
            body = json.loads(raw)
            body['model'] = 'jev-1.14.0' if model == 'jev-latest' else model
            raw = json.dumps(body).encode()
        return status, raw

    assert social.refresh_social(out, DAY, now=NOW, reservation=reservation,
                                 send=send, sleep=lambda _: None, fixture=True) == 'ok'
    bundle = export.validate_bundle(out)
    row = bundle['social/daily']['data'][0]
    assert requested == ['jev-1.13.0'] * 240
    assert row['model_versions'] == ['jev-1.13.0']
    assert row['sample']['eligible'] == 240
    assert row['sample']['exclusions']['classification'] == 0
    assert bundle['status']['data'][0]['state'] == 'fresh'
    assert bundle['social/credits']['data'][0]['closed']


@pytest.mark.parametrize('model', ['', None, [], {}, True, 1.5, 10**100,
                                   'unusual\u2028model', 'jev-latest', 'jev-1.14.0'])
def test_unreviewed_models_keep_strict_check(model, capsys):
    body = response()
    body['model'] = model
    diagnostic = {}
    with pytest.raises(ValueError, match='^SOCIAL_CLASSIFICATION_FAILED$'):
        social.classification_response(body, diagnostic)
    assert diagnostic == {'code': 'SOCIAL_CLASSIFICATION_FAILED', 'check': 'model'}
    with pytest.raises(ValueError, match='^SOCIAL_CLASSIFICATION_FAILED$'):
        social.classify([post()], key='fiction', enforce_bound=True, diagnostic=diagnostic,
                        send=lambda *args: (200, json.dumps(body).encode()))
    assert diagnostic['last_exclusion']['check'] == 'model'
    assert capsys.readouterr().err.endswith('check=model\n')
