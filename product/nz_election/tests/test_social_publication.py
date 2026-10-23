"""Exercise the workflow publisher entry point against an offline bare repository."""
import importlib
import json

import pytest

from product.nz_election.pipeline import export, social
from product.nz_election.pipeline.publish import DATA, git
from product.nz_election.tests.test_social import DAY, NOW, fixture


@pytest.mark.parametrize('published', [False, True])
@pytest.mark.parametrize('spent_before_run', [True, False])
def test_social_cap_publication_exit(tmp_path, monkeypatch, published, spent_before_run):
    publisher = importlib.import_module('product.nz_election.pipeline.publish')
    out, remote = tmp_path / 'bundle', tmp_path / 'remote.git'
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    fixture(out, reserve=not published)
    publisher.publish(out, remote, family='social')
    before = {name: git(remote, 'show', 'data:' + str(DATA / name)).stdout
              for name in ('social/credits.json', 'social/credits.csv') +
              (('social/daily.json', 'social/daily.csv') if published else ())}
    if spent_before_run:
        result = social.refresh_social(out, DAY, now=NOW, reserve=True,
                                       send=lambda *a: pytest.fail('spent day must not send'))
        assert result == 'budget-spent'
    else:
        calls = []
        def send(*args):
            calls.append(1)
            return (503, b'') if len(calls) == 1 else (200, b'{"tweets":[],"has_next_page":false}')
        assert social.refresh_social(out, DAY, now='2026-10-18T03:00:00Z', send=send,
                                     sleep=lambda _: None) == 'ok'
        assert len(calls) == 24
    expected = publisher.status_of(export.validate_bundle(out), 'social')
    real_publish = publisher.publish
    monkeypatch.setattr(publisher, 'publish', lambda bundle, repository, **kw: real_publish(bundle, remote, **kw))
    monkeypatch.setattr(publisher.sys, 'argv', ['publish', '--family', 'social', '--bundle', str(out)])
    monkeypatch.setenv('GITHUB_TOKEN', 'offline-test-token')
    monkeypatch.setenv('GITHUB_REPOSITORY', 'offline/test')
    monkeypatch.delenv('GITHUB_STEP_SUMMARY', raising=False)
    for name in ('GIT_CONFIG_COUNT', 'GIT_CONFIG_KEY_0', 'GIT_CONFIG_VALUE_0'):
        monkeypatch.setenv(name, '')
    publisher.main()
    status = json.loads(git(remote, 'show', 'data:' + str(DATA / 'status.json')).stdout)['data'][0]
    assert status == expected
    assert status['error_code'] is None
    if spent_before_run:
        assert status['state'] == ('stale' if published else 'unavailable')
        assert status['last_success_at'] == (NOW if published else None)
        assert status['message'] == "Day's collection cap was already spent; " + ('showing data through 2026-10-16' if published else 'no earlier sample is published.')
        for name, content in before.items():
            assert git(remote, 'show', 'data:' + str(DATA / name)).stdout == content
    else:
        assert status['state'] == 'fresh'
        assert status['last_success_at'] == '2026-10-18T03:00:00Z'
        assert '23 of 24 hours sampled' in status['message']
        daily = json.loads(git(remote, 'show', 'data:' + str(DATA / 'social/daily.json')).stdout)['data'][0]
        assert len(daily['provenance']['windows']) == 23
        assert daily['sample']['returned'] == 0
