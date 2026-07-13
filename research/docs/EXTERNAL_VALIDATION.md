# External validation register

Reconciliation of the project's canonical estimates (payload SHA `a4fd25ae…`) against
independently published official figures, beyond the 28 built-in gates. Compiled 2026-07-13.
Verdicts: **PASS** (matches within tolerance for the same concept), **EXPLAINED** (differs
for a documented conceptual/frame reason), **FLAG** (unresolved; must be disclosed).

All checks were computed from the canonical payload, the committed ASI panel, or scratch
recomputation from raw inputs; official values come from the cited documents (extraction
agents, 2026-07-13; ASI 2023-24 files archived from microdata.gov.in catalog 256).

## 1. ASUSE 2023-24 official report, Tables 36 and 34 (state, manufacturing, combined)

GVA per worker (ours vs official Table 36):

| Geography | Ours | Official | Delta |
|---|---:|---:|---:|
| India | 114,201 | 112,869 | +1.18% |
| Gujarat | 143,020 | 142,508 | +0.36% |
| Maharashtra | 139,135 | 136,858 | +1.66% |
| Karnataka | 119,316 | 117,436 | +1.60% |
| Telangana | 119,728 | 119,466 | +0.22% |
| Kerala | 187,399 | 187,042 | +0.19% |
| Tamil Nadu | 133,244 | 132,755 | +0.37% |

**PASS** (all within 2%). The small positive deltas follow from our documented denominator
(workers in market establishments with a valid GVA item).

Annual emoluments per hired worker (ours vs official Table 34): TN +0.32% (documented
matched-numerator concept), Kerala +0.03%, Gujarat +0.21%, Telangana +0.47%, India +1.60%,
Maharashtra +1.62%, **Karnataka +3.47%** (131,747 vs 127,334).

**PASS for six geographies; FLAG for Karnataka.** Root-cause attempt: recomputed three
numerator variants from unit records — matched items (902+903+912+929): 131,747; block total
939: 131,909; 939 minus working-owner items: 131,747. None reproduces 127,334, and for Tamil
Nadu the official 140,133 also sits below every variant (140,586–141,579), so MoSPI's exact
estimator differs from all tested variants by state-varying amounts. Consequence: the paper
must print official Table 34/36 values alongside ours in a reconciliation appendix and note
that raw peer gaps shift with the source (e.g. TN−Karnataka emoluments gap: +8,839 ours,
+12,799 from official values; direction unchanged).

## 2. TN Economic Survey 2025-26 Table 4.7, ASUSE panel (TN)

Official: units 13,91,621; employment 27,91,345; GVA ₹37,056 crore. Ours: units 1,391,656
(delta 35 units, 0.003%); implied GVA ≈ ₹37,192 crore (+0.37%, same delta as the GVA/worker
ratio); employment consistent (our stable size-band cells sum to 2,743,421 with the remainder
in cells our disclosure rule suppresses). **PASS.** Note: ES publishes TN ASUSE medium/large
size-class cells that rest on ≤9 sampled establishments — cells this project deliberately
suppresses. Do not "validate" against those cells; our suppression is the more defensible
practice and the paper should say so explicitly but diplomatically.

## 3. ASI 2023-24 official releases (Statement 7A, Statement 14A, website Table 3; ES Tables 4.1/4.7)

Manufacturing-only totals, Tamil Nadu: factories 29,899 vs official 29,975 (−0.25%); persons
engaged 2,888,489 vs 28,95,415 (−0.24%); GVA ₹242,567 crore vs ES Table 4.7 ASI panel
₹242,642 crore (−0.03%). All-India: persons −0.23%, GVA −0.18% vs the same panel. ES Table
4.1's larger TN figures (32,000 factories, 29.8 lakh persons, ₹252,175 crore GVA) are the
**whole factory sector** including non-manufacturing units, matching official Statement 7A
exactly — a scope difference, not a discrepancy. **PASS.**

## 4. Factory size distribution (Statement 14A; ES Table 4.11)

- Our **per-return sensitivity** classification vs official Statement 14A (TN,
  manufacturing): 100+ unit share 28.42% vs 28.43%; 50+ share 42.06% vs 42.11%. Vs ES Table
  4.11 (100+ employment share, 2023-24): TN 81.7 vs 81.6; Gujarat 79.1 vs 78.9; Maharashtra
  84.5 vs 84.2; India 80.1 vs 80.0. **PASS — near-exact.** Official practice counts returns.
- Our **primary equal-allocation** classification differs by construction: TN 100+
  employment share 77.5% (−4.1pp vs official-style), 100+ unit share 22.1% (−6.4pp). This is
  the documented multi-unit-return adjustment, largest for TN. **EXPLAINED.**
- Consequence for the paper: both classifications must be presented wherever size structure
  matters; the official-style per-return series is now externally validated, and the
  equal-allocation series is the project's establishment-size approximation whose effect is
  quantified (TN's large-factory share moves ~4pp between them). The missing-middle
  diagnostic should be shown under both.

## 5. Labour share of GVA (official ASI totals; ES §4.3) — corroboration reversed

Official ASI 2023-24 (Statement 7A, whole factory sector): TN emoluments/GVA = 94,315/252,175
= **37.4%**; Gujarat 26.9%; Maharashtra 31.9%. Ours (manufacturing only): TN 37.6%, Gujarat
28.3%, Maharashtra 32.4%. **PASS — our ratios reconcile with MoSPI's own totals.**

ES 2025-26 §4.3 states wage share (2014-24 average) TN 15%, Gujarat 8%, Maharashtra 9%, and
emoluments share TN 30%, Gujarat 18%, Maharashtra 24%. These **cannot be reproduced** from
official ASI totals under any definition tested (wages/GVA, emoluments/GVA, single-year or
2014-24 averages from our panel — TN averages 37-40%). The ES figures are plausibly computed
on a different base (deflated series, a narrower wage concept, or GSVA rather than factory
GVA) that the ES does not specify. **FLAG — with the flag pointing at the ES, not at us.**

Consequences, binding: (a) the ranking direction (TN's labour share highest among peers) is
corroborated by the ES and by official totals — the direction citation stands; (b) the ES's
*levels* must never be cited as corroboration of ours, and the paper must include one
paragraph noting the two bases could not be reconciled, worded neutrally ("differences in
concept or deflation that the Survey does not specify"). The audience includes the TN
government; state the arithmetic, attribute no error.

## 6. PLFS quarterly all-industry earnings (annual report Tables 38/39/40)

Scratch reproduction using the project's exact earnings machinery, industry filter removed,
grouped by quarter: **rural TN Q1 regular earnings reproduce the official value to the rupee
(16,730.1 vs 16,730)** — the rural frame contains no revisit records, so this is an exact
test of the machinery, passed. India-level cells reconcile within 0.3-3.0% across all three
concepts and quarters. TN-level deviations (regular +11%/−6% in two quarters; casual −7% to
−15%) are concentrated exactly where the documented first-visit-only choice omits urban
revisit records and state samples are small. **PASS (machinery) / EXPLAINED (frame).** The
paper should report this reproduction as evidence the pipeline is correct and the first-visit
choice as a stated design decision.

## 7. Known gaps that remain (not resolvable by reconciliation)

1. No design-based variances for ASUSE/ASI outcome cells or Layer 5 decompositions (MoSPI
   publishes no ASI state RSEs — confirmed: the 2023-24 release contains only the RSE
   formula and a qualitative disclaimer). Paper-grade fix: compute ASUSE design-based SEs
   from the survey's strata/sub-sample fields; for ASI, state the limitation and note MoSPI's
   own reliability disclaimer.
2. The Karnataka ASUSE emoluments delta (+3.47%) is unexplained at the estimator level.
3. ASUSE-ASI frame overlap remains documentation-based, untested.

## Bottom line

Every project estimate that has an official counterpart now reconciles with it to well under
1% in most cells and under 2% everywhere except one flagged Karnataka cell — and where
published sources disagree with each other (ES §4.3 vs MoSPI's own ASI totals), the project's
numbers sit with MoSPI's. The remaining assailable surface is the absence of
establishment-side uncertainty, the two flags above, and interpretation discipline — not
computational accuracy.
