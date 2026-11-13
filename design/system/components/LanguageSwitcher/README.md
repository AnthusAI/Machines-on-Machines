The language control in the top bar, and the banner that welcomes a visitor in the language their browser prefers. Two components that share one list of languages.

**LanguageSwitcher**

- **Provide**: `alternates` (the page in each language it exists in, itself included: `{ tag, name, url }`, from the page's language group), and `current` (the page's tag). `label` is the word "Language" in the page's language.
- Write each language's name in its own language and script ("English", "Español", "中文"), never as a flag, never translated.
- The control is a `panel`-colored pill with the Lucide `languages` icon and the current language's name; it opens a list of links. Every link has `lang` and `hreflang`.
- The current language is marked by its name in the control, a check mark and `aria-current`, never by color alone.
- List only languages the page exists in. A language with no page for this page is absent; never link to another page as if it were a translation. A page with no translation has no switcher.
- Place it in the bar between the destinations and the menu button, so it is always reachable. On a phone the bar shows the icon alone (48px, with the language in its accessible name) and the full list is also the last block of the full-page menu, in the same 72px blocks as the destinations.

**LanguageBanner**

- A flat `machine` strip above the page, in the visitor's language: a sentence, Switch now (`brand`), Stay here and Pause, and a 15 second countdown with a progress bar that is a flat fill, not a line. Three modes: `offer`, `read` (a quiet "Read in English" link for a visitor who prefers the site's primary language: never a countdown toward the primary) and `note` ("Switched to 中文" with Undo, after a remembered choice).
- The site script fills and shows it (`assets/mom-language.js`); the component here is for review. It is drawn before the page's content, hidden and empty, so nothing moves when it appears.
- With reduced motion the bar is not drawn and nothing fades; the number still counts down in text.
- On a phone the buttons share one row and Pause is its icon alone, so the strip stays short.
