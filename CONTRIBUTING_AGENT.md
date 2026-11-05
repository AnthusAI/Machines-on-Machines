# Kanbus planning

Install the CLI with `pip install kanbus` (version 0.41.0 or later). The Rust `kbs` CLI supports equivalent commands.

The shared board uses `.kanbus.yml` and issue prefix `MOM`. Use the CLI for all issue and event access; preserve the guard files under `project/`.

```bash
kanbus list --all --full-ids
kanbus show <id>
kanbus list --parent <epic-id>
kanbus create "Task title" --type task --parent <epic-id> --description "Task details"
kanbus dep <task-id> blocked-by <prerequisite-id>
kanbus validate
```

Record agent provenance on `create` and `comment` with `--agent-platform`, `--agent-model` and `--agent-name`, or the matching `KANBUS_AGENT_*` environment variables. Record meaningful implementation decisions and review results in issue comments.

Keep planning epics and their implementation tasks open until that work is actually completed. The branding plan uses one epic and an ordered list of tasks; its outstanding copy and design decisions belong in the first task. It needs neither a milestone nor behavior stories.

Commit board changes and their event history together. `kanbus commit` stages and commits `project/issues/` and `project/events/`; include any accompanying configuration or planning-document changes in the same planning update. Push planning-only changes to `develop`. Follow `AGENTS.md` for implementation review and release policy.

Markdown under `project/wiki/` may be edited directly. Use `kanbus wiki lint` to check its links.
