"""Verify immutable captures before joining official data by structural identity."""
import csv
import hashlib
import io
import json
from pathlib import Path
from . import xml_parser

ROOT = Path(__file__).resolve().parents[1] / "fixtures"


def captures(root=ROOT, paths=None):
    manifest = json.loads((root / "manifest.json").read_text())
    result = {}
    for entry in manifest["entries"]:
        path = entry["path"]
        if paths is not None and path not in paths:
            continue
        target = root / path
        if target.is_symlink() or not target.resolve().is_relative_to(root.resolve()):
            raise ValueError("UNSAFE_CAPTURE_PATH")
        if not target.is_file():
            raise ValueError(f"MISSING_CAPTURE: {path}")
        raw = target.read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
            raise ValueError(f"CAPTURE_HASH_MISMATCH: {path}")
        result[path] = raw
    if paths is not None and set(result) != set(paths):
        raise ValueError("MISSING_CAPTURE: " + ", ".join(sorted(set(paths) - set(result))))
    return result


def require_equal(left, right, context):
    if left != right:
        raise ValueError(f"FIXTURE_2023_MISMATCH: {context}: {left} != {right}")


GOLDEN_PATHS = {'ec-2023/' + name + '.csv' for name in ('party-quotients', 'party-votes', 'lists-successful', 'lists-unsuccessful', 'winners')} | {'ec-2023-xml/' + name + '.xml' for name in ('election', 'parties', 'candidates', 'electorates')}


def golden(root=ROOT):
    raw = captures(root, paths=GOLDEN_PATHS)
    def xml(name):
        return xml_parser.document(raw[f"ec-2023-xml/{name}.xml"], name)
    refs = xml_parser.references(*(raw[f"ec-2023-xml/{n}.xml"] for n in ("parties", "electorates", "candidates")))
    xml_parser.election(raw["ec-2023-xml/election.xml"], refs)
    def rows(name):
        return list(csv.reader(io.StringIO(raw[f"ec-2023/{name}.csv"].decode("utf-8-sig"))))
    parties = {p.attrib["p_no"]: p.findtext("party_name") for p in xml("parties")}
    by_name = {name: p for p, name in parties.items()}
    election = xml("election").find("parties")
    if election is None:
        election = xml("election")
    official = {p.attrib["p_no"]: p for p in election.findall(".//party")}
    for p in xml("parties"):
        if p.attrib["p_no"] in official:
            for tag in ("party_name", "short_name"):
                by_name[p.findtext(tag).strip()] = p.attrib["p_no"]
    vote_rows = rows("party-votes")
    header = vote_rows[1]
    totals = [r for r in vote_rows[2:] if r and r[0] == "Combined Totals"]
    require_equal(len(totals), 1, "national rows")
    for name in header[1:18]:
        if name not in by_name:
            raise ValueError(f"FIXTURE_2023_MISMATCH: unknown party {name}: 1 != 0")
    votes = {by_name[name]: int(totals[0][i]) for i, name in enumerate(header)
             if name in by_name}
    require_equal(sum(votes.values()), 2851211, "CSV valid votes")
    require_equal(sum(int(p.findtext("votes")) for p in official.values()), 2851211, "XML valid votes")
    require_equal(sum(int(p.findtext("total_seats")) for p in official.values()), 122, "XML house")
    for p, v in votes.items():
        require_equal(v, int(official[p].findtext("votes")), f"votes {p}")
    candidates = list(xml("candidates"))
    ranks = {}
    for c in candidates:
        rank = int(c.findtext("list_no"))
        if rank:
            key = (c.findtext("party"), rank)
            require_equal(key in ranks, False, f"duplicate rank {key}")
            ranks[key] = c
    lists = {}
    list_rows = {}
    for name in ("lists-successful", "lists-unsuccessful"):
        party = None
        for row in rows(name)[1:]:
            if not row or not row[0].strip():
                continue
            if not row[0].strip().isdigit():
                party = by_name[row[0].strip()]
                lists[party] = []
                continue
            rank = int(row[0])
            require_equal(rank, len(lists[party]) + 1, "list rank")
            c = ranks.get((party, rank))
            if c is None:
                raise ValueError(f"FIXTURE_2023_MISMATCH: list rank {party}/{rank}: 1 != 0")
            lists[party].append(c.attrib["c_no"])
            list_rows[c.attrib["c_no"]] = row
    require_equal(sum(map(len, lists.values())), len(ranks), "list candidate coverage")
    electorates = {e.findtext("electorate_name"): e.attrib["e_no"] for e in xml("electorates")}
    winners = {p: [] for p in votes}
    for row in rows("winners")[2:]:
        if not row:
            continue
        party, electorate = by_name[row[2]], electorates[row[0]]
        matches = [c for c in candidates if c.findtext("party") == party
                   and c.findtext("electorate") == electorate]
        require_equal(len(matches), 1, f"winner {electorate}/{party}")
        c = matches[0]
        require_equal(row[6], "Yes" if int(c.findtext("list_no")) else "No", "winner list status")
        if row[6] == "Yes":
            require_equal(list_rows[c.attrib["c_no"]][2], row[0] + " Electorate", "list electorate")
        winners[party].append(c.attrib["c_no"])
    wins = {p: len(ws) for p, ws in winners.items()}
    for p in votes:
        require_equal(wins[p], int(official[p].findtext("candidate_seats")), f"electorate seats {p}")
    quotients = []
    qrows = rows("party-quotients")
    for row in qrows[3:]:
        if not row or not row[0].isdigit():
            continue
        for i in range(1, len(qrows[2]), 2):
            if int(row[i + 1]):
                quotients.append(dict(rank=int(row[i + 1]), party_id=by_name[qrows[2][i]],
                                      divisor=row[0], display=row[i]))
    quotients.sort(key=lambda q: q["rank"])
    return {"input": dict(partyVotes=votes, electorateWins=wins, lists=lists,
                          electorateWinners=winners, nonListWinners=[], baseSeats=120),
            "expectedListMembers": {p: [c for c in lists.get(p, [])
                                        if len(list_rows[c]) > 2 and list_rows[c][2].startswith("Seat Allocation ")]
                                    for p in votes},
            "expectedSeats": {p: int(official[p].findtext("total_seats")) for p in votes},
            "quotients": quotients, "partyNames": parties}
