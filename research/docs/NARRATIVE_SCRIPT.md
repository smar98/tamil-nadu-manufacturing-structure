# Narrative script (v1) — "India's factory state"

The authoritative story for the public site. Supersedes STORYBOARD.md's copy while inheriting
its claim contracts, denominators, caveats and citation duties — every claim here maps to a
storyboard section and must survive the final claim audit against the canonical payload.

## The story in three sentences

Tamil Nadu employs more factory workers than any state in India, yet each factory worker
there produces less value than in almost any peer state — and it is not because its firms are
too small or because it makes the wrong products. The gap lives inside comparable industries,
while Tamil Nadu's workers take home the largest share of the value that is created. The
state's current policy instruments reward getting bigger and hiring more — not the thing the
data says is scarce: value per person.

## Voice rules

- Every term of art is defined in plain words at first use, in text, not a tooltip.
- One idea per scroll step. The reader never sees a chart before the question it answers.
- Numbers in prose are rounded and humanised ("about ₹8.4 lakh per person per year"); exact
  values live in the exhibit and methods layer.
- Each section ends with a one-line handoff that creates the next section's question.
- Technical nuance is layered, never cut: every section has a "How we know" expandable
  carrying the estimand, denominator, suppression and uncertainty detail verbatim from the
  storyboard contracts.
- Never causal. "Is associated with", "remains after", "we cannot tell from this data why."

## Act I — The paradox (hook)

**Scroll-open (full viewport, one number counting up):**

> One in seven of India's factory workers works in Tamil Nadu. No state employs more.

**Then, as the reader scrolls, the counter panel gives way to a ranked strip:**

> But rank India's big manufacturing states by the value each factory worker helps create,
> and Tamil Nadu drops to the bottom of the list — about ₹8.4 lakh per person per year,
> against ₹13 lakh in Gujarat and ₹15 lakh in Maharashtra.

**Lede paragraph:**

> This site is about that gap: what it is, what it is not, and what — if anything — Tamil
> Nadu's industrial policy says about it. Everything here is computed from the Government of
> India's own surveys of 2023–24, cross-checked against the government's published tables,
> and shown with its uncertainty and its limits.

Exhibit: single sticky panel morphing counter → ranked dot strip (persons engaged rank vs
GVA-per-person rank). Numbers: our ASI manufacturing values (payload); prose may note TN's
official rank-1 status citing ASI 2023-24 Statement 7A / ES Table 4.1.

Handoff: *"To see where the gap comes from, you first have to know how India counts its
manufacturing — because no single survey can see all of it."*

## Act II — Three lenses (the survey map, made human)

Plain: India measures manufacturing with three instruments that see three different worlds.
ASUSE walks into workshops — the tailor, the grinding mill, 1.39 million establishments in
TN. ASI reads registered factories' returns — about 30,000. PLFS asks workers themselves.
The site keeps them separate deliberately: an official table this year merged two of them
into one; we show why they cannot be one ladder (a workshop is never observed "becoming" a
factory).

Exhibit: three illustrated cards with universe, unit, what-it-can't-see. No chart.

Handoff: *"Start with the workshops and factories themselves: is Tamil Nadu's problem that
its firms never grow to the middle?"*

## Act III — The suspect that isn't guilty (missing middle)

Plain setup: the most famous diagnosis of Indian manufacturing is the "missing middle" — lots
of tiny firms, a few giants, nothing in between. If true for TN, the fix is obvious and the
state already runs a subsidy for exactly that (scaling up). We test it rather than assume it.

The test, narrated: show the full size distribution (both surveys separately, establishment
share vs employment share — defined plainly: "share of places vs share of jobs"); then the
diagnostic across states under four different definitions of "middle."

The verdict, in plain words:

> Under every definition we tested, Tamil Nadu's middle looks normal or deep compared with
> its peers. Tiny workshops dominate counts everywhere in India — that is not a Tamil Nadu
> disease. And Tamil Nadu's unincorporated sector is unusually likely to be an employer at
> all: about one in five of its workshops has at least one hired worker, far above the
> national average.

Nuance layer (verbatim duties): ASI size approximation with both classifications shown (the
official-style one now validated to 0.01pp against MoSPI's own table), ASUSE suppressed upper
bands, ES Table 4.7 / ASI Statement 14A / DES Table 4.10 citations.

Handoff: *"If the middle isn't missing, maybe Tamil Nadu just makes the wrong things?"*

## Act IV — The mix defence (industry composition, and the fair test)

Plain setup: comparing garment-heavy TN with chemicals-heavy Gujarat is comparing garments
with chemicals. Show what TN makes (industry mix), then explain standardisation in one
sentence: *"So we re-run every comparison as if both states had the same industry mix — and
see how much of the gap survives."*

The verdict:

> Industry mix explains between a seventh and a half of the gap with Gujarat, Maharashtra
> and Karnataka, depending on how finely you slice the industries. The majority of the gap
> survives the fair test in every specification: within the same industries, a factory
> worker in Tamil Nadu is associated with substantially less value added than one in those
> states — in most industries, covering most of the workforce, and in every one of the last
> sixteen years. Against Telangana the story flips — Tamil Nadu's apparent pay advantage
> there is almost entirely its industry mix.

Robustness backing (ROBUSTNESS_WITHIN_INDUSTRY.md): within-component 54–86% across 7-group,
24-industry and industry×size specifications vs IN/GJ/MH/KA; TN below peer in 16–22 of ~23
industries (74–97% of employment); gap negative all 16 years 2008–2023; capital intensity a
partial channel only (electronics counterexample). The four unprovables (sub-NIC2
composition, prices, no decomposition SEs, no causal design) go in this act's "How we know".

Exhibit: the decomposition, one comparator at a time (never a league table), animated split
of raw gap → mix component + within component.

Nuance layer: Kitagawa method in plain words + formulas, common-support coverage, no
row-level CIs (and why), component-cell SEs where available, "under a common composition"
wording, pairwise-weights warning.

Handoff: *"A smaller pie, then. Now — who gets what slice of it?"*

## Act V — The workers' slice (the human centre; largest visual weight)

Three beats:

1. **The slice.** Labour's share of factory value added is higher in TN than in every
   comparator (+7 to +12 points) — workers take the largest slice of the smallest pie. This
   direction agrees with both MoSPI's own totals and the TN Economic Survey; levels shown are
   ours, reconciled to MoSPI (the ES uses an unspecified base — methods note, neutral tone).
2. **The pay.** Regular factory-sector monthly earnings: middling — near India's average,
   above Gujarat, below the southern peers and Maharashtra. Three earnings concepts kept
   visibly separate with intervals.
3. **The protections.** Half of TN's regular manufacturing workers have a written contract
   (50.4%), 55% paid leave, 53% a specified social-security benefit — better than India,
   Gujarat and Kerala, ten-to-twenty points behind Karnataka and Telangana. This is the
   section a policy reader will remember; give it the room.

Handoff: *"So what does the state's own policy say about value, pay and protection?"*

## Act VI — The instruments and the mismatch (policy, evidence-laddered)

Plain: what TN currently, verifiably runs — the scale-up capital subsidy (5%, ₹25 lakh cap),
the EPF payroll subsidy past 20 employees (₹24,000/employee/year, 3 years), sector missions,
₹2.5 lakh crore of MSME lending. Each with what government reports (money out, recipients)
and what nobody yet knows (whether any of it causes growth).

The finding, stated carefully:

> Tamil Nadu's verified current instruments reward getting bigger and hiring more. None of
> them states an objective for the things this data finds scarce or strong: value per
> person, wage levels, or the contract and benefit coverage where Tamil Nadu trails its
> southern neighbours. And since April 2025 the state has had no general industrial policy
> in force at all — the 2021 policy expired, and its successor is, so far, an announcement.

Interpretation labelled as interpretation; document quotes with printed pages; expired
targets shown as historical.

## Act VII — What we can't tell you (credibility close)

Short, honest: cross-sections can't see firms that tried to grow and failed, can't link a
worker to their factory, can't evaluate any subsidy. The exploratory appendix teaser (one
sentence: establishments that *report* problems are the bigger, more formal ones — a reason
to distrust easy constraint stories, not a finding about constraints). Then the methods
drawer: every estimand, every suppression, the external-validation register summarised
("where our numbers could be checked against the government's own, they match to within 2%,
and usually much closer"), reproducibility pointer.

## Layered-disclosure pattern (every act)

- Layer 1: headline + prose (layperson).
- Layer 2: the exhibit with its adjacent caveat and unweighted n (interested reader).
- Layer 3: "How we know" expandable — estimand, denominator, formulas, suppression rules,
  uncertainty method, source citations (professor/bureaucrat).

## Design direction (binding for implementation)

Visual identity: see DESIGN.md (original direction from fresh research; the earlier
"field-brief" default is retired). Structural invariants that survive any restyle: each
survey keeps one hue everywhere; the TN accent is constant across all exhibits; hand-built
SVG only; direct labelling over legends. Scrollytelling:
sticky exhibit panes with step-triggered state changes driven by IntersectionObserver — no
scroll-jacking, native scroll always; graceful no-JS fallback (all steps render stacked).
Every chart: axis labels, units, direct labelling over legends where possible, suppressed
cells rendered as hatched "not published (sample too small)", counts and survey-universe tags
visible. Motion: 200-400ms ease, transform/opacity only, `prefers-reduced-motion` respected.
Mobile-first checked at 360px. Static export compatible (GitHub Pages), no new runtime
dependencies.
