A public conversation: what it is about, its title, the latest message with its author, and how active it is.

- **Provide** the fields of `_data/home-page/threads.json`: `title`, `anchor` as words ("On a reference: …", "On a story: …"), `latest` (the latest message, clipped at a sentence), `author` (a public handle, or the role labels `Editor` and `AI`), `messages`, `lastAt`, the anchor's `image` (without one, `PlaceholderArt` seeded by `href`), and `href` to the thread page.
- The author badge follows the role: `AI` in `machine`, `Editor` in `human`, a handle on `paper`.
- Fed by the `threads` include, `select="recent"`. Two side by side on the home page; a list on the Conversations page.
- Thread pages are read-only until forum posting ships; do not promise readers they can reply.
