# Layer 5 field map and locked decisions

Checkpoint for raw and composition-adjusted Tamil Nadu peer comparisons. This file is authoritative for Layer 5 implementation. It contains aggregate definitions only; it does not contain respondent records or identifiers.

## Question and interpretation boundary

Layer 5 asks:

> Are aggregate state differences associated with industrial or establishment-size composition, or do outcome gaps remain after comparing states under a common composition?

The adjustment is descriptive. It is not a causal effect of industry, establishment size, policy, productivity, formalisation or firm growth. A remaining within-cell gap may reflect capital intensity, product mix, prices, worker characteristics, location, ownership and other unmeasured differences.

ASUSE, ASI and PLFS remain separate statistical universes. Never combine them into one estimate or rank their levels as if they measured the same population.

## Comparator set

Every raw outcome compares Tamil Nadu (`33`) separately with:

1. India (`IN`);
2. Gujarat (`24`);
3. Maharashtra (`27`);
4. Karnataka (`29`);
5. Telangana (`36`);
6. Kerala (`32`), labelled as a sensitivity comparator.

The four core state peers are Gujarat, Maharashtra, Karnataka and Telangana. Pairwise adjusted estimates use a different common distribution for each comparator and therefore must not be compared across comparator rows as a league table.

## Raw outcomes

Create a raw comparison for each outcome below whenever both overall source estimates are publishable.

| Outcome ID | Survey | Source | Unit | Raw gap fields |
|---|---|---|---|---|
| `gva_per_worker` | ASUSE | Layer 3 `value_addition.per_person_value` | current rupees per worker per year | difference, ratio, percent gap |
| `annual_emoluments_per_hired_worker` | ASUSE | Layer 3 `establishment_compensation`, concept `annual_emoluments` | current rupees per hired worker per year | difference, ratio, percent gap |
| `gva_per_person_engaged` | ASI | Layer 3 `value_addition.per_person_value` | current rupees per person engaged per year | difference, ratio, percent gap |
| `emoluments_per_paid_person_engaged` | ASI | Layer 3 compensation concept `emoluments` | current rupees per paid person engaged per year | difference, ratio, percent gap |
| `labour_cost_proxy_per_paid_person_engaged` | ASI | Layer 3 compensation concept `labour_cost_proxy` | current rupees per paid person engaged per year | difference, ratio, percent gap |
| `labour_cost_proxy_share_of_gva` | ASI | Layer 3 concept `labour_cost_proxy`, field of the same name | proportion | difference only |
| `regular_monthly_earnings` | PLFS | Layer 4 `worker_earnings` | rupees per month | difference, ratio, percent gap |
| `self_employment_30_day_gross_earnings` | PLFS | Layer 4 `worker_earnings` | rupees per 30 days, gross | difference, ratio, percent gap |
| `casual_person_day_earnings` | PLFS | Layer 4 `worker_earnings` | rupees per person-day | difference, ratio, percent gap |
| `written_contract` | PLFS | Layer 4 `worker_job_quality` | proportion | difference only |
| `paid_leave` | PLFS | Layer 4 `worker_job_quality` | proportion | difference only |
| `specified_social_security` | PLFS | Layer 4 `worker_job_quality` | proportion | difference only |
| `no_social_security` | PLFS | Layer 4 `worker_job_quality` | proportion | difference only |

`unknown_social_security` remains a data-quality category and is not a peer-performance outcome.

For a rupee outcome:

```text
absolute_gap = TN - comparator
relative_ratio = TN / comparator
relative_gap_percent = 100 * (relative_ratio - 1)
```

Ratios and percent gaps are `null` if the comparator estimate is not positive. For a proportion, `absolute_gap` is stored in proportion units and `gap_display_unit` is `percentage_points`; the displayed value is `100 * absolute_gap`. Do not calculate a ratio for a proportion.

A raw comparison is:

- `stable` if both source estimates are stable;
- `low_precision` if neither is suppressed and at least one PLFS estimate is low precision;
- `suppressed` if either source estimate or a required denominator is suppressed/non-positive.

Do not replace a suppressed estimate with zero or derive it as a residual.

## Raw PLFS uncertainty

Copy each side's published Layer 4 standard error, RSE and 95% interval into the raw comparison. Do not create a confidence interval or significance test for the gap in v1:

- Tamil Nadu and India are not independent because Tamil Nadu is part of the India estimate;
- a single rule should apply to every comparator row;
- the project has not implemented covariance-aware contrast variance.

Do not infer significance from whether two confidence intervals overlap.

## Adjustment outcomes and dimensions

Composition adjustment is limited to establishment-side per-person outcomes:

- ASUSE GVA per worker;
- ASUSE annual emoluments per hired worker;
- ASI GVA per person engaged;
- ASI emoluments per paid person engaged;
- ASI labour-cost proxy per paid person engaged.

`labour_cost_proxy_share_of_gva` is raw-only because its natural composition weights would be GVA shares, which may be non-positive in component cells and are not the person-denominator composition used by the other outcomes.

Allowed adjustment dimensions:

| Survey | Industry | Size | Industry × size |
|---|---|---|---|
| ASUSE | yes | yes | no |
| ASI | yes | yes | yes, subject to support gate | 
| PLFS | no | no | no |

PLFS adjustment is omitted, not deferred to an implementation choice. Support-only diagnostics found inadequate common coverage across the core peer set. Earnings cannot be linked to Block 5 enterprise size, and a casual person-day can contain two activities in different industries. Do not invent a PLFS fallback or impute cells.

ASUSE industry × size adjustment is omitted because common support falls below the publication threshold for several core comparisons. ASI industry × size adjustment is permitted because support diagnostics exceed the threshold for India and the four core peers; every pair must still pass the implemented gate. Kerala is expected to fail the ASI joint gate and must remain null if it does.

## Project broad-industry groups

These are analytical support groups, not an official NIC aggregation. Every NIC 2008 manufacturing division 10–33 appears exactly once.

| Group ID | Public label | NIC divisions |
|---|---|---|
| `food_beverage_tobacco` | Food, beverages and tobacco | 10, 11, 12 |
| `textiles_apparel_leather` | Textiles, apparel and leather | 13, 14, 15 |
| `wood_paper_printing_other_repair` | Wood, paper, printing, other manufacturing and repair | 16, 17, 18, 31, 32, 33 |
| `chemicals_petroleum_pharma_rubber` | Petroleum, chemicals, pharmaceuticals and rubber/plastics | 19, 20, 21, 22 |
| `minerals_metals` | Non-metallic minerals and metals | 23, 24, 25 |
| `machinery_electrical_electronics` | Computers, electrical equipment and machinery | 26, 27, 28 |
| `transport_equipment` | Motor vehicles and other transport equipment | 29, 30 |

Build these cells directly from unit records and apply the Layer 3 outcome-cell disclosure rule to each broad cell. Do not reconstruct a broad cell by adding published NIC2 cells, because a broad aggregate may be stable even when one constituent NIC2 cell is suppressed.

NIC2 support diagnostics were inspected before locking this grouping. NIC2 cells did not reach 95% common denominator coverage for ASUSE emoluments against Karnataka or Telangana, or for some ASI/Telangana outcomes. The seven groups pass the core-peer industry gate without using outcome values or gap directions to choose cells.

## Common size groups

Use four groups for composition adjustment:

| Group ID | Source Layer 1 bands |
|---|---|
| `1-9` | `1`, `2-4`, `5-9` |
| `10-49` | `10-19`, `20-49` |
| `50-249` | `50-99`, `100-249` |
| `250+` | `250+` |

ASUSE uses reported establishment workers. ASI uses only the primary equal-allocation approximation: persons engaged divided by reported units. Do not use the per-return sensitivity as an adjustment basis; it is not observed factory size. ASI `zero-unclassified` records are not assigned to a size group and count as uncovered denominator mass.

The four-group construction is required for ASUSE compensation because a one-worker HWE cell does not provide a useful hired-worker composition cell and finer upper-size cells are sparse. Do not change the groups separately by outcome or comparator.

## Support and suppression gate

Support diagnostics were calculated without inspecting cell outcome means or gap directions. Publish an adjustment only when all conditions hold:

1. every retained cell is stable under the existing Layer 3 outcome-cell rule in both Tamil Nadu and the comparator;
2. retained cells cover at least 95% of the full eligible outcome denominator in Tamil Nadu;
3. retained cells cover at least 95% of the full eligible outcome denominator in the comparator;
4. at least two common cells remain;
5. both retained denominator totals are positive;
6. every decomposition identity below is finite and passes tolerance.

The 95% threshold is a project publication safeguard, not an official MoSPI rule. It limits omitted denominator mass to at most 5% on each side. It was locked after support-only diagnostics and before computing or inspecting adjusted gaps.

A cell is retained only if it is stable in both geographies. Renormalise each geography's denominator weights over the retained common support. Never impute, pool a failed cell into a new ad hoc group, carry a value from another geography, or derive a suppressed value as a residual.

If a gate fails, retain the adjustment row with null estimate/component fields, coverage diagnostics, `stability = "suppressed"`, and an explicit reason. Do not drop a failed comparator silently.

## Pairwise symmetric standardisation and decomposition

For geography `g` and retained cell `k`:

```text
Y_gk = weighted outcome numerator
X_gk = weighted outcome-specific person denominator
r_gk = Y_gk / X_gk
w_gk = X_gk / sum_j(X_gj)       # renormalised within common support
q_k = 0.5 * (w_TN,k + w_C,k)   # symmetric pairwise common weight
```

The outcome-specific denominator is:

- ASUSE GVA: workers in market establishments with a valid GVA item;
- ASUSE emoluments: hired workers in eligible HWE establishments;
- ASI GVA: persons engaged;
- ASI emoluments and labour-cost proxy: paid persons engaged.

Calculate:

```text
common_support_tn = sum_k(w_TN,k * r_TN,k)
common_support_comparator = sum_k(w_C,k * r_C,k)
common_support_raw_gap = common_support_tn - common_support_comparator

standardized_tn = sum_k(q_k * r_TN,k)
standardized_comparator = sum_k(q_k * r_C,k)
adjusted_gap = standardized_tn - standardized_comparator

composition_component =
  0.5 * sum_k((w_TN,k - w_C,k) * (r_TN,k + r_C,k))

within_component =
  0.5 * sum_k((r_TN,k - r_C,k) * (w_TN,k + w_C,k))
```

Required identities:

```text
adjusted_gap = within_component
common_support_raw_gap = composition_component + within_component
```

The full-universe raw gap is reported separately and is not forced to equal the decomposition because up to 5% of each denominator may be outside common support.

Do not label `within_component` as a treatment effect, productivity effect or size effect. Public wording: “gap remaining under a common [industry/size/joint] composition.”

## Adjustment uncertainty

Layer 3 does not yet provide design-based variances for ASUSE or ASI outcome cells. Therefore adjusted estimates, gaps and components have no confidence intervals or significance tests in v1. Set `uncertainty_available = false` and explain why in metadata.

No adjusted PLFS estimate is published, so an adjusted PLFS confidence-interval method is not applicable. A worker model must not add one.

## Public payload schema

Add two arrays under `structure_v1`.

### `peer_comparisons_raw`

Each row contains:

```text
survey
year
outcome
outcome_label
outcome_family                 # value_addition, compensation, earnings, job_quality
unit
is_proportion
comparator_id
comparator_label
comparator_type                # country, core_peer, sensitivity

tn_estimate
comparator_estimate
absolute_gap
gap_display_unit
relative_ratio                 # rupee outcomes only
relative_gap_percent           # rupee outcomes only

tn_standard_error              # PLFS only
comparator_standard_error      # PLFS only
tn_rse                         # PLFS only
comparator_rse                 # PLFS only
tn_ci95_lower                  # PLFS only
tn_ci95_upper
comparator_ci95_lower
comparator_ci95_upper

stability                      # stable, low_precision, suppressed
suppression_reason
```

### `peer_comparisons_adjusted`

Each row contains:

```text
survey
year
outcome
outcome_label
unit
adjustment_dimension           # industry, size, industry_size
classification                 # project_broad_industry_7, common_size_4, broad_industry_7_x_common_size_4
comparator_id
comparator_label
comparator_type

full_raw_tn
full_raw_comparator
full_raw_gap
common_support_tn
common_support_comparator
common_support_raw_gap

tn_denominator_coverage
comparator_denominator_coverage
retained_cell_count
total_cell_count

standardized_tn
standardized_comparator
adjusted_gap
composition_component
within_component
decomposition_residual
uncertainty_available          # always false in v1

stability                      # stable or suppressed
suppression_reason
components                     # retained stable cells only; empty when suppressed
```

Each `components` entry contains:

```text
cell_id
cell_label
tn_cell_rate
comparator_cell_rate
tn_weight
comparator_weight
common_weight
cell_composition_component
cell_within_component
```

Only jointly stable component cells may appear. Do not include suppressed cell estimates or enough residual information to reconstruct them.

## Validation contract

Implementation is not complete until all checks pass:

1. every raw Tamil Nadu and comparator estimate exactly matches its source Layer 3 or Layer 4 overall row;
2. every expected outcome × comparator raw row exists, including an explicit suppressed row where needed;
3. industry groups cover NIC 10–33 exactly once;
4. size groups contain the declared Layer 1 bands exactly once and exclude `zero-unclassified`;
5. no adjustment exists for PLFS, ASUSE industry × size, or ASI labour-cost-proxy share of GVA;
6. every retained component is stable in both geographies;
7. Tamil Nadu weights, comparator weights and common weights each sum to one within floating tolerance;
8. denominator coverage is in `[0, 1]` and stable rows meet 0.95 on both sides;
9. standardized values equal the sum of common-weighted cell rates;
10. `adjusted_gap = within_component` within tolerance;
11. `common_support_raw_gap = composition_component + within_component` within tolerance;
12. `decomposition_residual` is no larger than `1e-8 * max(1, abs(common_support_raw_gap))`;
13. suppressed adjustment rows have null estimate/component fields and an empty `components` list;
14. raw proportion comparisons have null ratios; rupee ratios are null when the comparator is non-positive;
15. PLFS source intervals are preserved, but every derived gap interval is absent;
16. no respondent, household, FSU, district, dispatch, DSL or sample-establishment identifier is exported;
17. public and research JSON outputs remain byte-identical;
18. existing Layers 1–4 arrays and 28 validation gates remain unchanged except for metadata that declares Layer 5.

Build to a scratch directory first. Inspect aggregate row counts, support coverage and one decomposition identity before replacing canonical generated files.

## Support findings that motivated the lock

Aggregate-only diagnostics produced these accepted findings:

- Seven-group ASUSE GVA common support covers at least 98.74% of each core comparator denominator and 99.91% of Tamil Nadu's denominator.
- Seven-group ASUSE emoluments covers at least 95.29% of Tamil Nadu's and 97.74% of a core comparator's denominator; Telangana is the limiting core pair.
- Seven-group ASI GVA and emoluments cover 100% of both denominators for all core peers in the diagnostic.
- Four-group ASUSE size support covers at least 95.63% of Tamil Nadu's and 95.81% of each core comparator's relevant denominator.
- Four-group ASI size support exceeds 99.8% of Tamil Nadu's denominator and 99.8% of each core comparator's denominator; the small uncovered share is primarily `zero-unclassified`.
- Seven-industry × four-size ASI support exceeds 99% for the core peers in the tested GVA and emoluments outcomes. Every implemented outcome must still pass the 95% gate.
- PLFS industry and enterprise-size support is inadequate for a consistent adjusted peer panel. Depending on outcome and peer, common coverage falls well below 95%, including zero jointly publishable broad-industry cells for several Telangana comparisons.
- Kerala fails the tested ASI industry and joint support gates because transport-equipment cells are not jointly publishable; this is why every sensitivity row remains subject to the same mechanical gate.

The exploratory support diagnostics were run as temporary scratch scripts and are not build inputs. The implementation must calculate support from the canonical local survey inputs rather than read those temporary files.
