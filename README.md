# Machines on Machines

**Information About Information Systems.** An AI/ML publication about AI/ML, run as a semi-supervised automated newsroom on [Papyrus](https://github.com/AnthusAI/papyrus).

Machines on Machines is its own Papyrus site, with its own backend, newsroom app and corpus. It takes over the knowledge base and articles that were going to be published at read.p.apyr.us, and read.p.apyr.us will redirect here.

## Status

The design is finished; the site is not built yet. This repository holds:

- `design/system/`: the design system (brand README, tokens, React components with previews and guidelines).
- `design/canvas/`: every design artboard, from the first brainstorm rounds to the final pages and the public newsroom home page.
- `docs/handoff.md`: what was decided, how the design maps onto Papyrus, and the build and migration plan.
- `tools/build_tokens_css.py`: turns `design/system/tokens.json` into `design/system/tokens.css`.

The site itself (`papyrus.config.ts`, `web/`, `infra/`) is the next step; see [`AGENTS.md`](AGENTS.md) and [`docs/handoff.md`](docs/handoff.md).

## Viewing the design

- Design system, published: https://claude.ai/artifact/LGfY72em5iEuK4s75RrBH3
- Design canvas, published: https://claude.ai/artifact/7F8o1vLBgeBJAY6gnHSUrN

Both links are private to Anthus. The files here are the source of both.

Built by [Anthus AI Solutions](https://anth.us). MIT licensed.
