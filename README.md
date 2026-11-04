# Machines on Machines

**Information About Information Systems.** An AI/ML publication about AI/ML, run as a semi-supervised automated newsroom on [Papyrus](https://github.com/AnthusAI/papyrus).

Machines on Machines is its own Papyrus site, with its own backend, newsroom app and corpus. It takes over the knowledge base and articles that were going to be published at read.p.apyr.us, and read.p.apyr.us will redirect here.

## Status

Phase 1 of the site is built: the theme, the components, the pages and the fixtures. It is not deployed; the app shell does not exist yet (see [`infra/README.md`](infra/README.md)).

- `papyrus.config.ts`, `publication/`, `amplify/`: the Papyrus site definition (backend plugin `home-page`).
- `web/`: the publication. `projection.json`, `hooks.py` (the named hooks), `mom_components.py` (the design components in Python), `pages/` (home, wire, conversations, proposals, components), `css/site-theme.css`, `assets/`.
- `design/system/`: the design system. `tools/sync_design_assets.py` copies its stylesheets into `web/assets/`.
- `design/figures/`: how figures are drawn: the rules, the `diagram-design` style guide and a worked gallery. Start with its `README.md`.
- `tests/`, `features/`: Python tests and Gherkin scenarios. Fixtures are in `tests/fixtures/`.
- `docs/handoff.md`: the decisions and the build and migration plan.

## Preview locally

```bash
python3 tools/preview_local.py /tmp/out   # writes only to that directory
python3 -m unittest discover -s tests && behave features
```

Needs `pip install -r requirements-publication.txt behave`. Stories carry provenance in front matter (`drafting: {by: agent}`, `approval: {status: approved, by: Name}`, `editorsPick`, `authors`); quote the key `"on"` in YAML (`review: {actor: ai, "on": 2026-10-28}`) because an unquoted `on` is a boolean.

## Viewing the design

- Design system, published: https://claude.ai/artifact/LGfY72em5iEuK4s75RrBH3
- Design canvas, published: https://claude.ai/artifact/7F8o1vLBgeBJAY6gnHSUrN

Both links are private to Anthus. The files here are the source of both.

Built by [Anthus AI Solutions](https://anth.us). MIT licensed.
