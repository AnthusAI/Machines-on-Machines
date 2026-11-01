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
