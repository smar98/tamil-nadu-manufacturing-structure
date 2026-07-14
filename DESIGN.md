# Design — "India's factory state"

Original direction, 2026-07-14, synthesized from fresh research into The Pudding, NYT
graphics, FT visual journalism, Reuters Graphics, ProPublica and independent data essays
(findings in HANDOFF; agents' per-piece reports in session records). Supersedes every prior
default. PRODUCT.md governs audience and register (brand; the page is the product).

## The identity in one line

**A ledger that tells a story.** The site's positioning is "every number on screen
reconciles against the government's own published tables — and says so"; the visual language
makes that literal: ruled ledger lines, tabular numerals, and small printed reconciliation
marks under every exhibit. Verification is the aesthetic, not a footnote.

## Scene

A senior bureaucrat opens the link late at night on a laptop in Chennai; a professor skims
it between meetings in Cambridge; a layperson reads it on a phone on a train. All three are
*reading* — long-form, dense numbers, daylight or office light. That forces a light,
paper-like reading surface with high-contrast ink. One art-directed theme; no dark mode
(editorial pages are art-directed once, like print).

## Color

Strategy: **committed** — one saturated protagonist color carries the story; everything else
is ink, paper and greys, plus three muted survey hues used only as identity tags.

- `--paper-0: oklch(0.985 0.002 25)` — near-white, chroma ~0 (not the cream band).
- `--ink: oklch(0.22 0.015 25)` — near-black, warm-leaning.
- `--ink-2: oklch(0.42 0.01 25)` — secondary text (≥4.5:1 on paper).
- **Tamil Nadu / the gap: madder.** `--tn: oklch(0.46 0.155 27)` (#9c2623) — deep chay-root red.
  Grounded in the subject: chay root (*Oldenlandia umbellata*), grown on the Tamil coast,
  dyed the famous "Madras red" textiles — a manufacturing-history color, not a UI color.
  TN is always this hue, in every exhibit, and nothing else ever is.
- Comparator states: greys (`oklch(0.60 0 0)` fill / `0.45` text), direct-labelled. Fade,
  never delete: non-focus series stay visible at low emphasis so the grey-out itself is
  evidence (Pudding "Pockets" mechanic).
- Survey identity hues (tags, small multiples headers, methods chips — never competing with
  TN in the same chart): ASI factories `--asi: oklch(0.45 0.115 250)` (#145892, steel blue); ASUSE
  workshops `--asuse: oklch(0.50 0.115 140)` (#3c732f, workshop green); PLFS workers
  `--plfs: oklch(0.45 0.115 310)` (#694084, census violet). The four identity hues
  (tn/asi/asuse/plfs) pass the dataviz six-check validator (lightness band, chroma floor,
  CVD separation worst-pair ΔE 12.9 tritan with direct labels as secondary encoding,
  contrast ≥3:1 on paper).
- Semantic marks: reconciliation PASS `--check: oklch(0.50 0.10 155)`; FLAG
  `--flag: oklch(0.62 0.13 75)` (amber, reserved strictly for disclosed flags/suppressions).
- Act I is the one **drenched** moment: the opening viewport sets `--tn` as the surface with
  paper-colored type, then hands over to the paper ground for the read. The hook owns the
  color; the argument owns the ink.

## Typography

FT's functional split (Financier for voice, Metric for evidence), executed with non-cliché
open faces, self-hosted via `next/font`:

- **Narrative (argument): Source Serif 4** — display at 600/650 weight (clamp ceiling
  ≤5.5rem, letter-spacing ≥ −0.02em, `text-wrap: balance`), body at 400/1.65 line-height,
  measure 65–72ch. Handoff lines (the one-sentence bridges between acts) in italic.
- **Evidence (charts, tables, chips, source lines, methods): Libre Franklin** — the
  news-graphics Franklin lineage; chart annotation 13–14px/500, `font-variant-numeric:
  tabular-nums lining-nums` everywhere a number can appear in a column or a counter.
- Numbers inside narrative prose stay in the serif (they are being *argued*); numbers in
  exhibits are Franklin tabular (they are being *checked*).
- No eyebrows/kickers, no numbered section scaffolding. Act openings are a thin full-width
  ledger rule + large serif title; the acts' sequence is carried by the scroll itself.

## The ledger grammar (what makes it ours)

1. **Reconciliation marks.** Under every exhibit, a one-line Franklin source entry in the
   form: `⊙ ASI 2023-24 · matches Statement 7A within 0.25% · n = 29,899 factories`. PASS
   marks in `--check`, FLAG marks in `--flag` with the disclosed reason. This is ProPublica's
   "verification as an action with a disclosed result," printed on the page.
2. **Suppression as a designed element.** Suppressed cells render as hatched slots labelled
   "not published (sample too small)" — absence made visible, never blank.
3. **Assertive chart titles.** Every chart title states the finding ("Mix explains a third
   of the gap; the rest is within the same industries"), never the axes (FT rule). Axis
   detail lives in the subtitle.
4. **Unit declared before the chart.** Each exhibit's first appearance defines its unit in
   prose ("one dot is one state's factory average") before the reader sees it (Pudding
   "Democracy" mechanic).
5. **Same-object morphs.** Where a chart form might be unfamiliar (the decomposition split),
   the exhibit transforms an already-understood chart into it stepwise — the Act I counter
   morphs into the ranked strip; the Act IV raw-gap bar splits into mix + within — rather
   than cutting to a finished graphic (Lambrechts mechanic; also NYT "You Draw It" spirit:
   let the reader hold a belief, then test it).
6. **Annotated, not minimal.** Charts carry well-placed callout annotations tied to features
   (Burn-Murdoch: annotated charts beat minimalist ones for comprehension). No chartjunk;
   also no mute charts.

## Layout & scroll

- One idea per viewport. Sticky exhibit pane + stepped prose (IntersectionObserver, native
  scroll, no scroll-jacking) for Acts I, III and IV; inline figures for Acts II, V–VII.
  No-JS and reduced-motion: all steps render stacked, exhibits show final state.
- Grid: single reading column (max 68ch) with exhibits breaking to a wider measure
  (max 1080px); full-bleed only for Act I and the Act V labour-share moment.
- Thin ledger rules (1px, ink at 12%) structure sections; no cards, no boxes-in-boxes.
  "How we know" is a styled native `<details>` at the end of each act — Franklin, slightly
  smaller, full technical depth (estimand, denominator, suppression, uncertainty, citations).
- Mobile-first at 360px; charts reflow to stacked small multiples rather than shrinking.

## Motion

Purposeful, few, exhibit-level: the Act I count-up (once, on view), the Act IV gap-bar
split, dot-strip re-ranks (FLIP transforms). 250–400ms, ease-out-quart, transform/opacity
(plus clip-path for the bar split). Everything visible by default; motion enhances, never
gates content. `prefers-reduced-motion`: crossfade or instant.

## Accessibility

WCAG 2.1 AA per PRODUCT.md: body ≥4.5:1, graphical objects ≥3:1 (madder on paper passes
both), no color-only encodings (TN also bolder stroke + direct label), full keyboard paths
for `<details>` and any toggles, text alternatives per chart, focus-visible rings in `--tn`.

## Anti-checklist (from the loaded craft bans + retired defaults)

No cream/warm-paper band; no Field Brief tokens; no side-stripe borders; no gradient text;
no uppercase tracked eyebrows; no numbered section markers; no hero-metric template; no
identical card grids; no legends where direct labels fit; no league tables of states (one
comparator at a time in Act IV); no "SHOCKING gap" register — the ledger never shouts.

## 2026-07-14 additions (from Sanchit's full-page voice-note review)

- **Madras check motif.** His idea, adopted: a single-hue woven check (crossing
  thread lines in madder) is the act separator (`.act-rule`), and a barely-there
  two-direction weave overlays the drenched hero (`.hero::before`). Single hue
  only — multicolour plaid would tip into costume. The hatch remains reserved
  for suppression; the check is structural, never semantic.
- **The finding, up front.** A BLUF panel directly after the hero (`.bluf`):
  the whole argument in one paragraph, then a numbered route map of the seven
  sections (`.route`). The numbers are a real sequence (the argument's order),
  which is what earns them.
- **Section rail.** Fixed left rail (`.siterail`) on ≥1360px viewports,
  JS-only, hidden while the hero is on screen (unreadable over madder).
  Narrative labels, not headings: "Not the missing middle", "Same industries,
  less value".
- **Scrolly geometry.** Steps are now full-viewport flex-centred
  (`min-height: 92svh; justify-content: center`), so the active step sits level
  with the vertically-centred sticky exhibit. This was the alignment complaint.
- **Instrument cards.** Policy instruments render as a 2×2 grid
  (`.instrument-grid`): name, one-line design, evidence-ladder chips, and the
  documents' figures behind a native `<details>`. Border-top rules, not boxes.
- **Reconciliation lines.** `.recon` is now one item per line (column flex) —
  the wrapped-flex version packed unevenly.
- **Currency.** Rupee figures in prose carry USD in brackets (₹83/USD, FY24
  average, noted in colophon). Chart labels stay rupee-only — dual-currency
  tick labels collide.
