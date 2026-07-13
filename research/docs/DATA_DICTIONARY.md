# Data Dictionary

The public payload is `public/data/manufacturing-structure.json`. It contains aggregate records only. Survey-weighted estimates are explicitly named; `sample_count` and other sample fields are unweighted.

## Legacy headline fields

| Field | Definition | Unit |
| --- | --- | --- |
| `unincorporated_establishments` | Published Tamil Nadu manufacturing establishments in ASUSE scope | count |
| `own_account_share` | OAE establishments divided by all ASUSE manufacturing establishments | proportion, 0-1 |
| `hired_worker_share` | HWE establishments divided by all ASUSE manufacturing establishments | proportion, 0-1 |
| `registered_factories` | Estimated active manufacturing reported units in the legacy ASI calculation | count |
| `workers_per_establishment` | Weighted ASUSE workers divided by weighted establishments | people per establishment |
| `persons_per_factory` | Weighted ASI persons engaged divided by weighted reported units | people per reported unit |
| `gva_per_worker` | Annual current-price GVA divided by ASUSE workers | rupees per year |
| `gva_per_person_engaged` | Annual current-price GVA divided by ASI persons engaged | rupees per year |

The `asuse_sectors`, `asi_sectors` and `plfs` keys are retained for compatibility with the existing interface. New analytical work is under `structure_v1`.

## `structure_v1` shared fields

| Field | Definition |
| --- | --- |
| `survey` | `asuse`, `asi`, or `plfs` |
| `year` | Survey reference label, currently `2023-24` |
| `geography_id` | `IN` for India or the two-digit State/UT code |
| `geography_label` | Human-readable geography |
| `geography_type` | `country` or `state` |
| `sample_unit` | Sample establishments, sample returns, or sample workers |
| `sample_count` | Unweighted records contributing to the cell |
| `stability` | `stable` or `suppressed`; Layer 4 also uses `low_precision` |
| `suppression_reason` | Null for stable cells; explicit rule triggered for suppressed cells |

Suppressed estimates and shares are `null`, not zero. Layer 4 also nulls the standard error, RSE and confidence interval.

## Establishment size

`structure_v1.establishment_size` contains ASUSE and ASI size distributions.

| Field | Definition |
| --- | --- |
| `classification` | Survey-specific size construction |
| `classification_label` | Full description of the construction |
| `size_band` | `1`, `2-4`, `5-9`, `10-19`, `20-49`, `50-99`, `100-249`, `250+`, or ASI `zero-unclassified` |
| `estimated_units` | Weighted establishments or reported units |
| `unit_share` | Cell units divided by geography/classification units |
| `estimated_employment` | Weighted workers or persons engaged |
| `employment_share` | Cell employment divided by geography/classification employment |

ASI classifications:

- `equal_allocation_approximation`: persons engaged divided by reported units; every unit on a multi-unit return receives the same average size.
- `per_return_sensitivity`: persons engaged per sample return; not observed factory size.

## Missing-middle diagnostics

`structure_v1.middle_diagnostic` aggregates the size distributions under four predeclared definitions: `10-249`, `10-99`, `20-249` and `50-249`. A diagnostic is suppressed if any required constituent size band is suppressed.

## Industry employment

- `structure_v1.industry_employment`: weighted employment by NIC2 for India and Tamil Nadu.
- `structure_v1.size_industry_employment`: weighted employment by NIC2 and size for India and Tamil Nadu.

`nic2` is the NIC 2008 two-digit division, restricted to 10-33. `industry_label` is its short label.

## PLFS worker-side enterprise size

`structure_v1.plfs_enterprise_size` is worker-weighted and is not an establishment count.

| Field | Definition |
| --- | --- |
| `size_code` | PLFS reported enterprise-size code: 1, 2, 3, 4, or 9 |
| `size_label` | Fewer than 6; 6-9; 10-19; 20+; or unknown |
| `worker_share` | Weighted share of usually working manufacturing people in the code |

## Layer 3 value addition

`structure_v1.value_addition` contains one row per survey, geography and dimension cell.

| Field | Definition |
| --- | --- |
| `dimension` | `overall`, `size`, or `industry` |
| `per_person_label` | `GVA per worker in market establishments` for ASUSE or `GVA per person engaged` for ASI |
| `per_person_value` | Ratio of weighted annual current-price GVA to the survey-specific weighted person denominator |
| `gva_contribution_share` | Cell GVA divided by sibling-cell GVA; null for overall rows and for every group containing a suppressed sibling |
| `denominator_positive` | Whether the aggregate person denominator is positive |
| `weighted_denominator_concentration` | Largest observation’s share of the weighted person denominator |
| `absolute_weighted_numerator_concentration` | Largest observation’s share of absolute weighted GVA |

ASUSE includes only records with market-establishment item 769 for the value-addition outcome. ASI GVA uses the project’s F-J accounting reconstruction.

## Layer 3 establishment compensation

`structure_v1.establishment_compensation` uses three concepts:

| `concept` | Numerator | Denominator | Public label |
| --- | --- | --- | --- |
| `annual_emoluments` | ASUSE Level 10 items 902 + 903 + 912 + 929, annualized | Formal + informal hired workers in HWE establishments | Annual emoluments per hired worker |
| `emoluments` | ASI wages and salaries + bonus | Paid persons engaged, Block E rows 6 + 7 + 8 | Emoluments per paid person engaged |
| `labour_cost_proxy` | ASI emoluments + provident-fund contribution + workmen/staff welfare | Paid persons engaged | Labour-cost proxy per paid person engaged |

Working-owner ASUSE items 901 and 911 are excluded because working owners are not in the hired-worker denominator. The ASI broad proxy is not take-home pay because welfare expenditure is not necessarily cash received by workers.

| Field | Definition |
| --- | --- |
| `per_person_value` | Ratio of weighted compensation numerator to weighted matched person denominator |
| `compensation_contribution_share` | Cell numerator divided by the sibling-group numerator; null if any sibling is suppressed |
| `labour_cost_proxy_share_of_gva` | ASI broad labour-cost proxy divided by aggregate GVA; present only for `labour_cost_proxy` and null when GVA is non-positive or too concentrated |
| `aggregate_gva_positive` | Whether aggregate GVA is positive for the proxy-share calculation |

## Layer 4 worker earnings

`structure_v1.worker_earnings` uses current weekly status and contains three separate concepts:

| `concept` | Estimate | Unit | Recall period |
| --- | --- | --- | --- |
| `regular_monthly_earnings` | Mean positive regular wage/salaried earnings in a manufacturing CWS activity | rupees per month | preceding calendar month |
| `self_employment_30_day_gross_earnings` | Mean non-zero gross self-employment earnings, retaining reported losses | rupees per 30 days (gross) | last 30 days |
| `casual_person_day_earnings` | Mean positive manufacturing casual earnings after summing two qualifying activities within a person-day | rupees per person-day | previous 7 days |

Earnings have `overall`, `sex` and `sector` rows. They are not published by enterprise size because Block 6 earning activities are not linked to the Block 5 enterprise-size response.

## Layer 4 worker job quality

`structure_v1.worker_job_quality` covers usual-status regular wage/salaried manufacturing workers, using employed principal-activity particulars before subsidiary particulars. Concepts are `written_contract`, `paid_leave`, `specified_social_security`, `no_social_security` and `unknown_social_security`. The three social-security concepts use the same codes 1-9 denominator and sum to one when all three are published. Each is assessed independently, so a rare unknown category may be suppressed while the specified-benefit and official no-benefit rates remain available. Dimensions are `overall`, `sex`, `sector` and `enterprise_size`; size category `9` is unknown.

Overall rows cover India and all available States/UTs. Subgroup rows cover India, Tamil Nadu, Gujarat, Maharashtra, Karnataka, Telangana and Kerala. The male category follows the official convention and includes sex codes 1 and 3.

## Layer 4 common fields

| Field | Definition |
| --- | --- |
| `concept`, `concept_label` | Machine-readable concept and public label |
| `dimension` | `overall`, `sex`, `sector`, or, for job quality only, `enterprise_size` |
| `category_id`, `category_label` | Dimension category; overall rows use `all` |
| `estimate` | Weighted mean or proportion; null when suppressed |
| `unit`, `recall_period` | Measurement unit and reference period/concept |
| `sample_unit` | `persons` or `person-days` |
| `sample_count` | Unweighted valid denominator observations |
| `active_fsu_count` | Distinct active FSUs contributing denominator observations; no FSU identifier is exported |
| `kish_effective_n` | Weight-based effective sample size, `(sum w)^2 / sum(w^2)` |
| `maximum_weight_share` | Largest observation’s share of denominator weight |
| `maximum_weighted_outcome_share` | Largest absolute weighted earnings contribution; earnings only |
| `unweighted_yes_count`, `unweighted_no_count` | Sampled binary outcomes and non-outcomes; rates only |
| `standard_error`, `rse` | Official paired-subsample standard error and relative standard error |
| `ci95_lower`, `ci95_upper` | 95% interval; proportions are clipped to 0-1 and positive-only earnings lower bounds to zero |
| `stability` | `stable` at RSE ≤20%, `low_precision` at 20-30%, otherwise `suppressed`, subject to all hard rules |
| `suppression_reason` | Semicolon-separated hard-rule failures, or null |

## Layer 5 raw peer comparisons

`structure_v1.peer_comparisons_raw` contains one row for each of 13 outcomes and each comparator: India, Gujarat, Maharashtra, Karnataka, Telangana and Kerala. ASUSE, ASI and PLFS remain separate.

| Field | Definition |
| --- | --- |
| `outcome`, `outcome_label` | Machine-readable outcome and public label |
| `outcome_family` | `value_addition`, `compensation`, `earnings`, or `job_quality` |
| `unit` | Source outcome unit |
| `is_proportion` | Whether the outcome is a 0-1 proportion |
| `comparator_id`, `comparator_label` | India or peer geography |
| `comparator_type` | `country`, `core_peer`, or `sensitivity` |
| `tn_estimate`, `comparator_estimate` | Exact Layer 3 or Layer 4 overall source estimates |
| `absolute_gap` | Tamil Nadu estimate minus comparator estimate |
| `gap_display_unit` | Source rupee unit, or `percentage_points` for a proportion |
| `relative_ratio` | Tamil Nadu divided by comparator for rupee outcomes with a positive comparator; otherwise null |
| `relative_gap_percent` | `100 * (relative_ratio - 1)` where the ratio exists |
| `tn_standard_error`, `comparator_standard_error` | Copied Layer 4 source standard errors for PLFS; null otherwise |
| `tn_rse`, `comparator_rse` | Copied Layer 4 source RSEs for PLFS; null otherwise |
| `tn_ci95_lower`, `tn_ci95_upper` | Copied Tamil Nadu Layer 4 interval for PLFS; null otherwise |
| `comparator_ci95_lower`, `comparator_ci95_upper` | Copied comparator Layer 4 interval for PLFS; null otherwise |
| `stability` | `stable`, `low_precision`, or `suppressed` from the two source sides |
| `suppression_reason` | Source side and reason when either required estimate is unavailable |

No confidence interval, standard error, RSE or significance test is produced for the derived gap.

## Layer 5 adjusted peer comparisons

`structure_v1.peer_comparisons_adjusted` contains pairwise symmetric industry, size and permitted ASI industry × size standardisations. `classification` is `project_broad_industry_7`, `common_size_4`, or `broad_industry_7_x_common_size_4`.

| Field | Definition |
| --- | --- |
| `adjustment_dimension` | `industry`, `size`, or `industry_size` |
| `full_raw_tn`, `full_raw_comparator`, `full_raw_gap` | Full-universe source estimates and raw gap; null when the adjusted row is suppressed |
| `common_support_tn`, `common_support_comparator` | Geography-specific rates after renormalising own weights over retained cells |
| `common_support_raw_gap` | Difference between the two common-support rates |
| `tn_denominator_coverage`, `comparator_denominator_coverage` | Retained denominator divided by the full eligible outcome denominator |
| `retained_cell_count`, `total_cell_count` | Jointly stable positive-denominator cells retained and declared cells available |
| `standardized_tn`, `standardized_comparator` | Cell rates averaged with the symmetric pairwise common weights |
| `adjusted_gap` | Standardized Tamil Nadu minus standardized comparator |
| `composition_component` | Symmetric composition contribution to the common-support raw gap |
| `within_component` | Gap remaining under the common composition; equals `adjusted_gap` within tolerance |
| `decomposition_residual` | `common_support_raw_gap - composition_component - within_component` |
| `uncertainty_available` | Always `false` in v1 |
| `components` | Retained jointly stable cells; empty for a suppressed row |

Each `components` entry contains `cell_id`, `cell_label`, `tn_cell_rate`, `comparator_cell_rate`, `tn_weight`, `comparator_weight`, `common_weight`, `cell_composition_component` and `cell_within_component`. Suppressed cell estimates and residual information that could reconstruct them are not included.

A stable adjusted row requires at least two retained cells, at least 95% denominator coverage on both sides, positive retained totals and finite decomposition identities within tolerance. Failed rows keep coverage and cell counts but null all estimate/component fields and use an empty `components` list. There is no PLFS adjustment, ASUSE industry × size adjustment, or adjustment of ASI labour-cost-proxy share of GVA.

## Validation

Each top-level validation record stores the reconstructed value, official published value, error, tolerance, tolerance basis where applicable, and status. Layer 4 uses absolute half-rounding-unit tolerances and exact sample-count matches. Layer 5 leaves the 28 published-table records unchanged and is covered by focused payload-contract checks. The canonical builder writes no payload unless all gates pass.
