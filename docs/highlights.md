# Highlights for skimming readers

Write `==phrase==` in an article, post or wiki body and Markus renders `<mark>phrase</mark>`. The site styles it as a rounded `human` fill with heavier (600) text; see `design/system/components/Highlight/README.md` for the look and why.

```markdown
A shop owner may choose to install the robot. ==Employees and customers will be the ones it sees on its rounds.== Nobody asked them first.
```

It nests with other inline Markdown:

```markdown
==a *key* claim with [a source](https://example.com)==
```

## When to use it

- Highlight the phrase a reader who skims should leave with: a key claim, a number, a decision.
- At most about one or two per section. If everything is highlighted nothing is.
- Never a whole paragraph, a heading, a caption or a pull quote's text. Prefer a phrase to a full sentence when the sentence has a throat-clearing opening.
- A highlight is the editor's choice: it should say what the article's argument needs a skimmer to know, not decorate.
- The meaning never rests on colour. Do not write "the highlighted text" as a way to point at it; say what it says.
