"""Temporary publication checkouts must not leave automatic Git writers running."""
import importlib

import pytest

from product.nz_election.tests.test_pipeline import make_bundle, repository

publisher = importlib.import_module('product.nz_election.pipeline.publish')


@pytest.mark.parametrize('seeded', [False, True])
def test_publish_checkout_disables_automatic_git_work(tmp_path, monkeypatch, seeded):
    if seeded:
        remote = repository(tmp_path, make_bundle(tmp_path))
    else:
        remote = tmp_path / 'remote.git'
        remote.mkdir()
        publisher.git(remote, 'init', '--bare', '-q')
    bundle = make_bundle(tmp_path, 2)
    original = publisher.git
    checkouts = set()
    commands = set()

    def checked_git(root, *args, **kwargs):
        if root != remote and args[0] not in {'init', 'config'}:
            for key, value in (('gc.auto', '0'), ('maintenance.auto', 'false'),
                               ('gc.autoDetach', 'false')):
                assert original(root, 'config', '--local', '--get', key).stdout.strip() == value
            checkouts.add(root)
            commands.add(args[0])
        return original(root, *args, **kwargs)

    monkeypatch.setattr(publisher, 'git', checked_git)
    result = publisher.publish(bundle, remote)
    assert result['outcome'] == 'published'
    assert {'ls-remote', 'commit', 'push'} <= commands
    assert ('fetch' in commands) == seeded
    assert len(checkouts) == 1
    assert all(not checkout.exists() for checkout in checkouts)
