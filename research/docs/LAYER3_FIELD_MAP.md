# Layer 3 field map and locked decisions

Checkpoint for the 2023–24 value-addition and establishment-compensation build. This file contains aggregate definitions only; it does not contain respondent records or identifiers.

## ASUSE

| Measure | Source | Public denominator | Public label |
|---|---|---|---|
| Annual GVA | Level 08 item 769, annualized with Level 03 reference-period fields | Level 09 item 789 total workers | GVA per worker in market establishments |
| Annual emoluments | Level 10 items 902 + 903 + 912 + 929, annualized with the same factor | Level 09 items 782 + 783 formal and informal hired workers; HWE only | Annual emoluments per hired worker |

- The matched numerator includes formal-hired pay, informal-hired pay, formal-hired social contributions and common employer amenities. It excludes working-owner items 901 and 911 because working owners are not in the hired-worker denominator.
- Item 939 includes those working-owner amounts. Dividing item 939 by hired workers reconstructs ₹141,579, 1.03% above published Table 34; the matched numerator reconstructs ₹140,586, 0.32% above the published ₹140,133. The definition is chosen for numerator-denominator alignment, not merely benchmark proximity.
- Item 769 is market-establishment GVA. Non-market item 779 is NVA and is not combined with it.
- `total_workers` and hired-worker counts are persons/positions, not full-time equivalents.
- Ratios are ratios of weighted totals, never averages of establishment-level ratios.
- Verified against `research/data/raw/asuse_2023_24_vol2.txt:1744-1761` and published Table 34 in `asuse_2023_24_report.txt:32690-32732`.
- New Tamil Nadu manufacturing reconciliation target: annual emoluments per hired worker ₹140,133; hired workers 1,078,944; HWE establishments 272,663.

## ASI

| Measure | Source | Public denominator | Public label |
|---|---|---|---|
| Annual GVA | Existing F–J reconstruction in `build_asi_aggregates.py` | Block E row 10 total persons engaged | GVA per person engaged |
| Emoluments | Block E total wages and salaries + bonus | Paid persons engaged: rows 6 + 7 + 8, equivalently row 10 minus row 9 | Emoluments per paid person engaged |
| Broad labour-cost proxy | Emoluments + provident-fund contribution + workmen/staff welfare | Paid persons engaged | Labour-cost proxy per paid person engaged |

- Block E row 9 is unpaid family members/proprietors/cooperative members and has no wage, bonus, fund-contribution, or welfare entries. It is included in row 10, so row 10 is appropriate for GVA per person engaged but not for compensation per paid person.
- The broad proxy includes welfare expenditure that may not be cash received by workers. It must not be labelled take-home pay.
- GVA is output minus intermediate input, not profit or compensation.
- Verified against `research/data/raw/asi/schedule05.pdf`, extracted text lines 110-140, and `build_asi_aggregates.py:172-225,386-446`.
- Reuse `build_factory_frame()` for F–J monetary formulas, but merge its outcomes onto the validated A/E frame from `asi_structure_frame()` so non-positive weights or reported-unit counts cannot be silently replaced.

## Public aggregation contract

- Surveys remain separate.
- Produce overall state comparisons, size comparisons, and NIC2 comparisons. Do not build size × NIC2 outcomes in this chunk.
- ASI size uses the existing equal-allocation approximation and the existing per-return sensitivity. ASUSE uses reported establishment workers.
- Publish ratios and contribution shares, not respondent records or identifiers.
- Suppress an outcome cell if sample count is below 10, or if one record contributes more than 70% of the weighted denominator or absolute weighted numerator.
- Suppressed values are `null`, never zero.
- Publish contribution shares only when every sibling cell in that geography/dimension/classification group is stable; otherwise set all shares in that group to `null` to prevent residual reconstruction.
- Ratios with non-positive denominators are `null`. ASI labour-cost-to-GVA ratios are `null` when aggregate GVA is non-positive.
