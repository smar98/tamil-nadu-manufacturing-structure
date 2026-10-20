# External validation register

This register reconciles the project's estimates against independently published official figures, beyond the 28 built-in reconciliation gates. It was compiled on 2026-07-13 against the canonical payload with SHA-256 `eef71cb8be3eb468e1bd020b8cfce3ee592baba1b7e2da72a8e937a782239ba9`.

Verdicts: **PASS** (matches within tolerance for the same concept), **EXPLAINED** (differs for a documented conceptual or frame reason), **FLAG** (unresolved; disclosed here).

Estimates were computed from the canonical payload, the committed ASI panel, or a recomputation from the raw inputs. Official values come from the cited documents (extracted 2026-07-13). The ASI 2023-24 files were taken from microdata.gov.in catalog 256.

## 1. ASUSE 2023-24 official report, Tables 36 and 34 (state, manufacturing, combined)

GVA per worker (ours vs official Table 36):

| Geography | Ours | Official | Delta |
| --- | ---: | ---: | ---: |
| India | 114,201 | 112,869 | +1.18% |
| Gujarat | 143,020 | 142,508 | +0.36% |
| Maharashtra | 139,135 | 136,858 | +1.66% |
| Karnataka | 119,316 | 117,436 | +1.60% |
| Telangana | 119,728 | 119,466 | +0.22% |
| Kerala | 187,399 | 187,042 | +0.19% |
| Tamil Nadu | 133,244 | 132,755 | +0.37% |

**PASS** (all within 2%). The small positive deltas follow from the denominator used here: workers in market establishments with a valid GVA item.

Annual emoluments per hired worker (ours vs official Table 34): Tamil Nadu +0.32% (matched-numerator concept, see METHODOLOGY.md), Kerala +0.03%, Gujarat +0.21%, Telangana +0.47%, India +1.60%, Maharashtra +1.62%, **Karnataka +3.47%** (131,747 vs 127,334).

**PASS for six geographies; FLAG for Karnataka.** Three numerator variants were recomputed from unit records: matched items (902+903+912+929) give 131,747; block total 939 gives 131,909; and 939 minus working-owner items gives 131,747. None reproduces 127,334. For Tamil Nadu the official 140,133 also sits below every variant (140,586 to 141,579), so the official estimator differs from all tested variants by amounts that vary by state. This register lists the official Table 34 and 36 values beside ours. Raw peer gaps shift with the source. The Tamil Nadu minus Karnataka emoluments gap is +8,839 on our figures and +12,799 on official values. The direction is unchanged.

## 2. Tamil Nadu Economic Survey 2025-26, Table 4.7, ASUSE panel (TN)

Official: units 13,91,621; employment 27,91,345; GVA ₹37,056 crore. Ours: units 1,391,656 (delta 35 units, 0.003%); implied GVA about ₹37,192 crore (+0.37%, the same delta as the GVA-per-worker ratio); employment is consistent, since the stable size-band cells sum to 2,743,421 with the remainder in cells that the disclosure rule suppresses. **PASS.**

The Survey publishes Tamil Nadu ASUSE medium and large size-class cells that rest on 9 or fewer sampled establishments. This project suppresses cells with fewer than 10 sampled establishments, so those cells are not used for validation.

## 3. ASI 2023-24 official releases (Statement 7A, Statement 14A, website Table 3; ES Tables 4.1 and 4.7)

Manufacturing-only totals, Tamil Nadu: factories 29,899 vs official 29,975 (-0.25%); persons engaged 2,888,489 vs 28,95,415 (-0.24%); GVA ₹242,567 crore vs ES Table 4.7 ASI panel ₹242,642 crore (-0.03%). All-India: persons -0.23% and GVA -0.18% against the same panel. ES Table 4.1's larger Tamil Nadu figures (32,000 factories, 29.8 lakh persons, ₹252,175 crore GVA) cover the whole factory sector, including non-manufacturing units. They match official Statement 7A exactly. The difference is one of scope. **PASS.**

## 4. Factory size distribution (Statement 14A; ES Table 4.11)

- The **per-return sensitivity** classification against official Statement 14A (Tamil Nadu, manufacturing): 100+ unit share 28.42% vs 28.43%; 50+ share 42.06% vs 42.11%. Against ES Table 4.11 (100+ employment share, 2023-24): Tamil Nadu 81.7 vs 81.6; Gujarat 79.1 vs 78.9; Maharashtra 84.5 vs 84.2; India 80.1 vs 80.0. **PASS, near-exact.** Official practice counts returns.
- The **primary equal-allocation** classification differs by construction: Tamil Nadu 100+ employment share 77.5% (-4.1 points against the official-style series), 100+ unit share 22.1% (-6.4 points). This is the multi-unit-return adjustment, which is largest for Tamil Nadu. **EXPLAINED.**

Both classifications are reported. The per-return series is externally validated and matches official practice. The equal-allocation series is the establishment-size approximation used in this project. Its effect is quantified: Tamil Nadu's large-factory share moves by about 4 points between the two.

## 5. Labour share of GVA (official ASI totals; ES §4.3): direction agrees, levels differ

Official ASI 2023-24 (Statement 7A, whole factory sector): Tamil Nadu emoluments/GVA = 94,315/252,175 = **37.4%**; Gujarat 26.9%; Maharashtra 31.9%. Our figures (manufacturing only): Tamil Nadu 37.6%, Gujarat 28.3%, Maharashtra 32.4%. **PASS.** Our ratios reconcile with MoSPI's own totals.

ES 2025-26 §4.3 states a wage share (2014-24 average) of Tamil Nadu 15%, Gujarat 8% and Maharashtra 9%, and an emoluments share of Tamil Nadu 30%, Gujarat 18% and Maharashtra 24%. These figures cannot be reproduced from official ASI totals under any definition tested (wages/GVA, emoluments/GVA, single-year or 2014-24 averages from our panel; Tamil Nadu averages 37-40%). The Survey probably uses a different base (a deflated series, a narrower wage concept, or GSVA rather than factory GVA), but it does not specify one. **FLAG (unresolved): the Survey's levels cannot be reproduced from official ASI totals.**

What this means for the reading: (a) the ranking direction, with Tamil Nadu's labour share highest among peers, agrees with the Survey and with official totals. The Survey can be cited for that direction. (b) The Survey's levels are not cited as corroboration of this project's levels. The two bases could not be reconciled, because of differences in concept or deflation that the Survey does not specify.

## 6. PLFS quarterly all-industry earnings (annual report Tables 38, 39 and 40)

Reproduction using the project's earnings method, with the industry filter removed and results grouped by quarter: **rural Tamil Nadu Q1 regular earnings reproduce the official value to the rupee (16,730.1 vs 16,730).** The rural frame contains no revisit records, so this is an exact test of the method, and it passes. India-level cells reconcile within 0.3-3.0% across all three concepts and quarters. Tamil Nadu-level deviations (regular +11% and -6% in two quarters; casual -7% to -15%) are concentrated where the first-visit-only choice omits urban revisit records and state samples are small. **PASS (method); EXPLAINED (frame).** This reproduction is evidence that the earnings pipeline is correct. The first-visit choice is a stated design decision (METHODOLOGY.md).

## 6b. ASUSE published RSEs (Tables 46-48): replication infeasible from public files

A full replication of MoSPI's published ASUSE RSEs was attempted on 2026-07-13, using the design-based approach described in METHODOLOGY.md. Point estimates and sample counts reproduce the published tables exactly. Table 46's Tamil Nadu establishment total matches to the rupee, and the sample n matches for all seven gate cells. The published RSEs miss by -0.70 to +4.74 points, in inconsistent directions. The likely cause is the official variance calculation, which uses listing-schedule (LSU) design information that is absent from the public ESU unit files. As a result, this project cites MoSPI's published RSEs as uncertainty context and publishes no project-computed establishment-side standard errors. The attempt is documented as a limitation of the public-use files. **EXPLAINED (a limitation of the public-use files; no data error).**

## 7. Known gaps that reconciliation does not resolve

1. There are no design-based variances for ASUSE or ASI outcome cells, or for the peer-comparison decompositions. For ASUSE this is a limitation of the public-use files (§6b): exact replication of MoSPI's RSEs requires non-public LSU data, so the published Tables 46-49 serve as the uncertainty context. For ASI, MoSPI publishes no state RSEs. The 2023-24 release contains only the RSE formula and a qualitative disclaimer.
2. The Karnataka ASUSE emoluments difference (+3.47%) is not explained at the estimator level.
3. Overlap between the ASUSE and ASI frames is documented but not tested.

## Summary

Where an official counterpart exists, the project's estimates reconcile within 2% except for the flagged Karnataka cell (§1). The explained differences are in §4 and §6. Two items remain unexplained: the Karnataka emoluments difference (§1, §7) and the Survey's levels (§5). The lack of establishment-side uncertainty is listed in §7.
