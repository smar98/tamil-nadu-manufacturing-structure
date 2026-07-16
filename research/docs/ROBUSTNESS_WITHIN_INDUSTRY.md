# Robustness of the within-industry GVA finding

`research/scripts/robustness_within_industry.py` tests whether Tamil Nadu's lower ASI GVA per
person engaged under a common broad-industry composition could be an artifact of industry mix,
classification granularity, one odd year or capital intensity. It is read-only and does not
change the payload or locked method.

## Verdict, stated honestly

**As a descriptive claim about ASI 2023-24, the finding is robust across the specifications
tested.** The within-industry component is the *majority* of the GVA-per-person-engaged gap
against India, Gujarat, Maharashtra and Karnataka in every specification tested (54–86%), the
gap is broad-based across industries rather than driven by any single one, and the complete
panel shows the same sign for sixteen consecutive years. This is not evidence for a causal or
efficiency interpretation. What remains unmeasured here: composition below the 2-digit
industry level (product mix inside an industry), price/deflator differences across states
(all values current-price), design-based uncertainty on the decompositions (no SEs computable, see `ASUSE_UNCERTAINTY_FIELD_MAP.md` §resolution and ASI's absence of published
state RSEs), and anything about *why* (cross-section, no causal design). The site's wording
stays "is associated with less value added within the same industries" with these four limits
in the methods layer.

## (a) Classification-granularity sensitivity

Symmetric Kitagawa decomposition of the ASI GVA-per-person-engaged gap re-run at 24 NIC
2-digit industries (the finest published granularity), with true employment weights
recomputed from the raw frame. The script requires at least one raw/payload comparison and fails if the maximum relative
deviation exceeds `1e-12`; the publication run produced 0.0. Cells are restricted to jointly
published (non-suppressed) payload cells; employment coverage of retained cells is 94.6–100%.

Within-component share of the common-support gap:

| Comparator | 7 groups (published) | 7×4 industry×size (published) | 24 NIC2 (this run) |
|---|---:|---:|---:|
| India | 75.6% | 67.5% | 65.4% |
| Gujarat | 67.2% | 55.8% | 54.0% |
| Maharashtra | 70.9% | 67.5% | 65.6% |
| Karnataka | 84.0% | 80.9% | 85.9% |
| Telangana | unstable — gap only ≈ ₹38–46k, component shares not meaningful | | |
| Kerala | suppressed (TN coverage <95%) | suppressed | TN *above* KL on common support |

Consequences for narrative wording: "mix explains only a sixth to a third of the gap" is no
longer safe across specifications (at NIC2 the mix share reaches 46% vs Gujarat). The safe,
still-strong claim: **industry mix explains between a seventh and a half of the gap depending
on comparator and granularity; the within-industry component is the majority in every
specification against every major comparator.** Breadth: TN's rate sits below the
comparator's in 21/24 cells (India), 16/24 (Gujarat), 22/23 (Maharashtra), 19/22 (Karnataka),
covering 74–97% of common-weight employment — not a one-industry story.

Kerala note (doc-only; not a site claim): Kerala's high aggregate GVA/worker is carried by
cells outside common support (petroleum refining is suppressed for concentration); within
common support TN is above Kerala in employment terms. The published suppression of the TN–KL
adjusted row stands; do not present this scratch quantity as a Layer 5 row.

## (b) Multi-year persistence (ASI panel, 2008–2023)

The panel output uses `-` for a lower Tamil Nadu value, `+` for a higher or equal value and `·`
when either side is missing. An all-years conclusion is printed only when every required pair is
observed. For the complete all-manufacturing series (calibration: TN 2023 = 839,770, exact to
the payload), Tamil Nadu is below Gujarat, Maharashtra and Karnataka in **all sixteen years
2008–2023** (2023 ratios
0.64, 0.55, 0.56). Telangana has four missing early pairs, so no all-years conclusion is
reported; among observed years the sign alternates, consistent with the small 2023-24 gap.
Kerala: TN above until 2010, below since 2011 (see refinery note).

Named sectors, 2020–2023: TN lower in all comparable years vs Maharashtra in
electrical-electronics, electronics-core, food-processing, leather-footwear, life-sciences
and textiles-apparel; vs Karnataka in five of those; vs Gujarat in food-processing,
life-sciences, textiles-apparel. TN's clear strength is automobiles (at or above every peer
except Maharashtra). The 2023-24 finding is not a one-year artifact.

## (c) Capital intensity (descriptive channel, not a confounder to "control away")

Fixed capital per employee, 2023, TN as ratio of peer: all-manufacturing **0.36× Gujarat,
0.57× Maharashtra, 0.55× Karnataka** — Tamil Nadu's factories are markedly capital-shallow.
Within sectors the pattern splits: textiles (0.61–0.76×), food processing (0.44–0.46×) and
life sciences (0.63–0.74×) are less capital-intense where they are less productive — there,
low capital per worker is a plausible proximate channel for the GVA gap. But
electrical-electronics runs **more** capital per employee than every peer (1.30–1.52× vs
GJ/MH/KA/TG) while producing 32–45% less value per person than those states, and
electronics-core runs more capital than Gujarat, Maharashtra and Telangana (1.36–1.95×;
Karnataka is the exception at 0.87×) while producing 39–43% less value than MH/KA/TG (parity
with Gujarat) — capital shallowness cannot be the whole story. Site treatment: capital intensity is presented as a descriptive
channel ("Tamil Nadu's factories work with about a third of Gujarat's capital per person"),
never as a completed explanation.

## (d) Already-published triangulation

The canonical payload already publishes industry×size-adjusted rows
(`broad_industry_7_x_common_size_4`) for all three ASI outcomes — the within-component
survives joint adjustment for industry *and* factory size (row above). No new computation
needed; cite the published rows.

## Decision

The battery supports centring the story on the descriptive gap that remains under a common
broad-industry composition. The methods layer states the unmeasured factors and uses the
mix-share range above.
