# Codex CLI notes (0.154.0, ChatGPT login, plan "prolite")

Researched 2026-10-15 from the docs (learn.chatgpt.com/docs), the openai/codex source and local
smoke runs. What `bin/codex-run` relies on:

- `codex exec` takes no `-a` or `--search`; use `-c 'approval_policy="never"'` and
  `-c 'web_search="live"'`. Live search works on this login (a `web_search` item appears in the
  JSONL). Under exec every approval request is auto-rejected, so `never` is the only sane policy.
- `--json` events: `thread.started`, `turn.started`, `turn.completed {usage}`, `turn.failed`,
  `item.*` with item types `agent_message`, `reasoning`, `command_execution`, `file_change`,
  `mcp_tool_call`, `collab_tool_call`, `web_search`, `todo_list`, `error`. Rate limits are not in
  the JSONL; they are in `~/.codex/sessions/YYYY/MM/DD/rollout-*<thread>*.jsonl` as
  `rate_limits.primary.used_percent` (window 10080 min). `--ephemeral` would suppress that file.
  Pro lite shows `secondary: null`: one weekly window, no five-hour window.
- Exit codes: 1 on bad config, missing prompt, or a failed or interrupted turn; else 0.
- About 19k input tokens is the per-turn floor (global AGENTS.md, skills, plugins), mostly cached.
- Sandbox: `workspace-write` writes in cwd plus temp dirs, `.git` stays read-only to the model,
  network off unless `sandbox_workspace_write.network_access=true`; `--add-dir` widens writes.
- Hooks: `<repo>/.codex/hooks.json` with `PreToolUse`, `PostToolUse`, `Stop`, `SessionStart` and
  friends; exit 2 or a `permissionDecision: deny` JSON blocks. Untrusted hooks are skipped
  silently under exec unless `--dangerously-bypass-hook-trust` (the `--hooks` flag here).
- Review: `codex exec review --base <branch>` reviews the branch diff with a fresh reviewer
  (web search and subagents off); output is text findings with file and line ranges.
- `exec resume <thread_id>` continues a thread; `exec fork <id>` copies one.
- AGENTS.md: `~/.codex/AGENTS.md` then repo root down to cwd, 32 KiB cap.
- Models in this account: `gpt-6-astra` (default, efforts low to ultra), `gpt-5.6-sol`,
  `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-reserve`; 272k context. `ultra` delegates to subagents.
- Multi-agent is on (`[agents]` config, `.codex/agents/*.toml`); subagents inherit the sandbox.
