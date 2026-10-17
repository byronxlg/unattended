#!/usr/bin/env bash
# Expected: last line "PASS classify: 2 classified, 1 excluded, check named". Classifies three
# posts through an injected transport: a valid response, a valid response whose choice is a tied
# argmax key that is not the mapping's first key, and a response missing one question.
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python - <<'PY'
import json
from product.nz_election.pipeline import social

def body(choice_party=None, drop=None):
    answers = {}
    for name, question in social.QUESTIONS.items():
        if question['type'] == 'noul':
            answers[name] = dict(type='noul', noul=0.9)
        elif question['type'] == 'choice':
            keys = list(question['criteria'])
            probs = {k: 0.0 for k in keys}
            if name == 'party' and choice_party:
                probs[keys[0]] = 0.5
                probs[choice_party] = 0.5
                answers[name] = dict(type='choice', choice=choice_party, probabilities=probs)
            else:
                probs[keys[0]] = 1.0
                answers[name] = dict(type='choice', choice=keys[0], probabilities=probs)
        else:
            probs = {str(i): 0.0 for i in range(5)}
            probs['2'] = 1.0
            answers[name] = dict(type='score', score=2, probabilities=probs)
    if drop:
        answers.pop(drop)
    return json.dumps(dict(model='jev-1.13.0', answers=answers, usage={})).encode()

tied = list(social.QUESTIONS['party']['criteria'])[1]
responses = iter([body(), body(choice_party=tied), body(drop='topic')])
def send(method, url, headers, data):
    return 200, next(responses)

posts = [dict(id=str(i), text=f'post number {i} about the election', author=dict(id=f'a{i}'), lang='en') for i in range(3)]
diagnostic = dict(window=None, attempt=None, http_status=None, code=None)
try:
    result, excluded = social.classify(posts, key='k', send=send, diagnostic=diagnostic)
except Exception as exc:
    print(f'FAIL classify: raised {exc.args[0] if exc.args else type(exc).__name__}; diagnostic keys {sorted(diagnostic)}')
    raise SystemExit(1)
other = {k: v for k, v in excluded.items() if k not in ('duplicate', 'unsupported', 'irrelevant')}
named = isinstance(diagnostic.get('check'), str) and diagnostic['check'] and 'post number' not in diagnostic['check']
ok = len(result) == 2 and sum(other.values()) == 1 and named
print(f"{'PASS' if ok else 'FAIL'} classify: {len(result)} classified, {sum(other.values())} excluded, check {'named' if named else 'unnamed'}")
raise SystemExit(0 if ok else 1)
PY
