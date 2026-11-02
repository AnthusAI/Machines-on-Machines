# Newsletter: The Weekly

The chosen design is **D · Front page** (canvas, Newsletter page). It is light mode, built from Papyrus's email template: a navy header band with the wordmark image and the list name, a white card, and a navy footer band.

- `email-theme.json` is the `theme` block for the `newsletter` plugin in `papyrus.config.ts`. Papyrus validates it with `theme_from_config`; a test here does too.
- The wordmark is an image, because mail clients drop web fonts: `web/assets/email/mom-wordmark-on-navy-2x.png` (646 by 136, shown at 323 by 68; the footer shows it at 150 wide).
- `sample-weekly.md` is a sample issue body in Markus. What makes it D rather than a plain roundup: the lead story's image at the top of its section, and a provenance line ("Drafted by AI · Approved by …", "Written by …") in italics under every story.
- Body type is Helvetica/Arial, not Archivo: most mail clients ignore web fonts.

## What Papyrus does today, and what D needs from it

The weekly roundup draft (`assemble-roundup`) writes linked titles and descriptions grouped by section. Until Papyrus adds the two pieces below, an editor adds them to the draft by hand before approving:

1. The lead story's image: the first story's `image` front matter as a Markus image above its title.
2. Each story's provenance line, in the site's attribution wording, as an italic line under its description.

Papyrus also switches branded emails to its own dark colors when the reader's system is dark; this design is light only.

## Turning the newsletter on

The plugin is not enabled yet. To enable it, add the `newsletter` plugin to `backend.plugins` in `papyrus.config.ts` with this theme, `sendingDomain` `mail.machines-on-machines.anth.us`, a `fromAddress` on that domain, the site's compute role ARN, a postal address, and a `weekly` roundup list with `archivePath` `/roundup/`. Then add the `roundup` section and `newsletter_issue` listing type to `web/projection.json` (Papyrus `docs/newsletter.md`, "Archive").
