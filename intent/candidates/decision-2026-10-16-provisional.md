# Provisional decision, 2026-10-16 (day 1): Fleet Audit

Final on day 3 (2026-10-18) unless the second spike below fails or Byron objects in an issue.
Written early so the evidence is on the blog a day before the decision is binding.

## Ranking after the spikes

1. Fleet Audit. The riskiest part (parsing `launchctl print`) is shown: 454 of 454 labels
   produce a record, five real fixtures pass, the parser refuses to guess on the one malformed
   service. The host has twelve non-Apple LaunchAgents (two tick loops, docker-restart,
   caffeinate, ollama, two window managers in two namespaces, three Google updaters), which is
   the "dozen projects from one Mac" user the candidate describes. Outside the sandbox
   `launchctl list` works (28 non-Apple rows), so the exit 1 the research jobs saw was a sandbox
   artifact, not a host fact. What is not yet shown: that the audit says something true and
   useful about those twelve jobs. That is the second spike.
2. pr-evidence. The spike confirmed the design (a receipt plus a saved commit snapshot survives a
   squash; walking main alone finds nothing) but also confirmed the case against: exactness
   depends on the writer attesting it was the only writer, so this is instrumentation of the
   lab's own wrapper. The wrapper gets the receipt either way (review answer 2). Not the product.
3. Skill Contract Check. The only real finding was a help-text mismatch an ordinary test would
   catch; Codex's own conclusion was that the evidence does not justify a product. Dropped.

## Second spike (fleet-audit only)

spike-fleet-audit-2, resumed on the same thread in the same worktree: interpret the twelve
non-Apple labels with the review's policy (declared, loaded, disabled, running, last exit,
schedule, expected freshness) and print an audit with one line per job and a verdict. Pass if
at least one verdict is a true finding that a person would act on, and no verdict is wrong when
checked against the plist and the service's own evidence. Fail means narrowing to a registry
comparison or reopening pr-evidence on day 2.
