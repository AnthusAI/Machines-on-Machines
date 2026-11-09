---
title: Durable execution is how long-running agents survive a crash
dek: A workflow engine remembers where an agent stopped, so a restart picks up the same thought.
date: 2026-10-26
tags: [DurableExecution, AgentEvals]
drafting: {by: agent, at: 2026-10-25}
approval: {status: approved, by: Ada Reader, at: 2026-10-26}
---

A fictional fixture story used only by tests and screenshots.

An agent that runs for hours will be interrupted. #DurableExecution records each step so the run can resume instead of starting over.

A restart is not a crash. The workflow engine stores the inputs and outputs of every step, so a restart replays what is known and only runs what is new.

The hard part is deciding what counts as a step. A step that talks to the outside world has to be safe to repeat, or it has to be recorded as done.

Editors see this as a question of trust. If an agent can pick up where it stopped, then a person can read the record and say whether it stopped in the right place.

None of this makes an agent right. It makes the agent's work inspectable, which is the property a newsroom needs before it lets software draft anything.

Teams that adopt it first usually find their agents were failing more often than they knew. The restarts were silent, and the repeated work was invisible.

That is the case for recording every step, whether or not anyone ever reads the record.
