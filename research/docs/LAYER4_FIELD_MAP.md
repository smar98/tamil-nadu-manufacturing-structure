# Layer 4 field map and locked decisions

Checkpoint for the PLFS 2023–24 worker-earnings and job-quality build. This file contains aggregate definitions only; it does not contain respondent records or identifiers.

## Statistical units and activity concepts

Layer 4 uses two distinct PLFS concepts and does not force them into one activity branch:

- **Earnings:** current weekly status (CWS), Block 6. Manufacturing is the industry of the earning activity in Block 6.
- **Job quality and enterprise size:** usual principal/subsidiary status, Block 5.1/5.2, with principal-activity precedence.

The outputs must not imply that a Block 6 earning activity is linked to the Block 5 enterprise-size response. Earnings-by-enterprise-size is therefore not published.

## Current-weekly earnings

| Concept | Universe and source | Public estimate | Public label |
|---|---|---|---|
| Regular wage/salaried earnings | CWS status `b6q5_perv1` in `31, 71, 72`; CWS industry `b6q6_perv1` in NIC divisions 10–33; positive `b6q9_perv1` | Weighted mean among workers reporting positive earnings | Monthly regular wage/salaried earnings |
| Self-employment gross earnings | CWS status in `11, 12, 61, 62`; CWS industry in NIC divisions 10–33; non-zero `b6q10_perv1`; retain reported losses | Weighted mean among self-employed persons reporting non-zero earnings | Gross self-employment earnings in the last 30 days |
| Casual earnings | Daily Block 6 status in `41, 42, 51`, daily NIC division 10–33, and positive daily earnings; sum two qualifying activities within a person-day | Weighted mean across qualifying person-days, counting a person-day once | Casual earnings per person-day |

- Regular earnings refer to the preceding calendar month.
- Self-employment earnings refer to the last 30 days and combine returns to labour, ownership and capital. They are not wages.
- Casual earnings refer to each of the previous seven days. A person may contribute more than one qualifying person-day.
- Preserve the three measures separately. Do not annualise or combine them into one average.
- Use first-visit `perv1.csv` consistently. Official state quarterly earnings tables also use urban revisits and are not direct benchmarks for this payload.
- `mult_perv1` is the analysis weight. Ratios are ratios of weighted totals.
- Zero is structural or not reported in the earnings fields and is not treated as an observed zero wage without the status/universe checks above.
- No documented top-code or earnings sentinel is present.

### Casual daily fields

For day suffixes `3pt1` through `3pt7`, use the first- and second-activity status, industry and earnings fields. Handle the public-file header exceptions explicitly:

- `b6q4_3pt2` and `b6q5_3pt2` omit `_perv1`;
- `b6q4_act2_3pt5_act2_perv1` contains an extra `act2`;
- `b6q5_3pt7` omits `_perv1`.

## Usual-status job quality

Select one employed usual-status branch per person:

1. Use principal fields if `b5pt1q3_perv1` is in `11, 12, 21, 31, 41, 51`.
2. Otherwise use subsidiary fields if `b5pt2q3_perv1` is in that set.
3. Never replace an employed principal activity with a subsidiary activity.

Headline job-quality estimates are restricted to manufacturing regular wage/salaried workers: selected status `31` and selected NIC `10000–33999`.

| Concept | Principal field | Subsidiary field | Numerator / denominator | Public label |
|---|---|---|---|---|
| Written contract | `b5pt1q11_perv1` | `b5pt2q10_perv1` | codes 2–4 / codes 1–4 | Has a written job contract |
| Paid leave | `b5pt1q12_perv1` | `b5pt2q11_perv1` | code 1 / codes 1–2 | Eligible for paid leave |
| Specified social security | `b5pt1q13_perv1` | `b5pt2q12_perv1` | codes 1–7 / codes 1–9 | Eligible for a specified social-security benefit |
| No specified social security | same | same | code 8 / codes 1–9 | Not eligible for a specified social-security benefit |
| Social security not known | same | same | code 9 / codes 1–9 | Social-security eligibility not known |

The three social-security shares use the same denominator and sum to one when all three are published. Code 9 is not silently recoded as eligible or ineligible. This matches the official Table 36 denominator; excluding code 9 does not reproduce the published no-benefit estimate. Each category is assessed independently under the worker-side precision rule, so a rare unknown category does not suppress the specified-benefit or official no-benefit headline.

The questionnaire also asks these questions of casual employees with statuses 41 and 51. Do not pool them with regular workers in the headline result.

## Enterprise size and subgroups

- Enterprise size: principal `b5pt1q10_perv1`, subsidiary `b5pt2q9_perv1`.
- Codes: `1` fewer than 6 workers; `2` 6–9; `3` 10–19; `4` 20+; `9` not known.
- Job quality by size intersects the regular-worker manufacturing universe with each size code. Unknown size remains an explicit category.
- Sex: official reconciliation groups codes `1` and `3` as male and code `2` as female. Public metadata must state that the male category follows the official convention and includes the very small transgender sample; do not publish code 3 separately.
- Sector: `b1q3_perv1`, rural `1` and urban `2`.
- Overall estimates cover India and all available States/UTs. Sex, rural/urban and enterprise-size breakdowns cover India, Tamil Nadu, Gujarat, Maharashtra, Karnataka, Telangana and Kerala.
- Do not publish fine state × industry × size × sex cells.

## Official design-based uncertainty

Use the official two-interpenetrating-subsample estimator rather than a generic independent-record standard error.

Required private calculation fields:

- state: `state_perv1`;
- sector: `b1q3_perv1`;
- NSS region: `nss_region_perv1`;
- stratum: `b1q5_perv1`;
- rural sub-stratum: `b1q6_perv1` for rural observations;
- interpenetrating sub-sample: `b1q11_perv1`, values 1 and 2;
- FSU/PSU: `b1q1_perv1`, used for support diagnostics only;
- weight: `mult_perv1`.

The annual design-stratum key is state × sector × NSS region × stratum × rural sub-stratum. Omit rural sub-stratum for urban records.

For every mean or proportion, write the estimate as:

```text
R = sum(weight * y) / sum(weight * x)
```

For design stratum `h` and sub-sample `m`, calculate weighted totals `Y_hm` and `X_hm`. The variance is:

```text
variance(R) =
  sum_h [((Y_h1 - Y_h2) - R * (X_h1 - X_h2)) ** 2]
  / (sum(weight * x) ** 2)
```

Then:

```text
standard_error = sqrt(variance)
ci95 = R ± 1.96 * standard_error
rse = standard_error / abs(R)
```

Clip proportion intervals to 0–1. Clip a positive-earnings mean's lower display bound to zero. A confidence interval is `null` if its denominator is non-positive, required design fields are invalid, either interpenetrating sub-sample is absent from a full design stratum, variance is non-finite, or the cell is suppressed.

Build the complete design scaffold before applying a domain indicator. A sub-sample with no domain observations contributes zero and is not dropped.

The implementation must reproduce Tamil Nadu's published rural manufacturing share of 12.17% and RSE of 5.81% before the interval helper is accepted.

## Worker-side publication rule

Do not reuse the establishment-side 10-observation/70%-concentration rule. A PLFS rate can have more than 100 observations and still be unusable because a positive or negative outcome is rare.

Hard-suppress the point estimate and interval when any condition holds:

1. fewer than 30 valid denominator observations;
2. fewer than 10 distinct active FSUs;
3. Kish effective sample size below 30, where `n_eff = sum(w)^2 / sum(w^2)`;
4. one observation supplies more than 20% of denominator weight;
5. the official paired-subsample variance cannot be computed;
6. design-based RSE exceeds 30%;
7. for a binary rate, fewer than 10 sampled outcomes or fewer than 10 sampled non-outcomes;
8. for an earnings mean, one person or person-day supplies more than 20% of absolute weighted earnings.

Classify a published cell as:

- `stable` when RSE is at most 20%;
- `low_precision` when RSE is above 20% and at most 30%;
- `suppressed` otherwise or when another hard rule triggers.

Suppressed estimates, standard errors and intervals are `null`, never zero. Diagnostic counts and non-identifying stability fields remain public.

## Public aggregation contract

Create two Layer 4 arrays under `structure_v1`:

- `worker_earnings`;
- `worker_job_quality`.

Every row includes, as applicable:

```text
survey = "plfs"
concept
dimension                    # overall, sex, sector, enterprise_size
geography_id
geography_label
category_id
category_label
estimate
unit
recall_period
sample_unit                  # persons or person-days
sample_count
active_fsu_count
kish_effective_n
maximum_weight_share
maximum_weighted_outcome_share   # earnings only
unweighted_yes_count             # rates only
unweighted_no_count              # rates only
standard_error
rse
ci95_lower
ci95_upper
stability
suppression_reason
```

No person, household, FSU, district or dispatch identifier is published.

## Validation targets

- Table 36: India and Tamil Nadu regular-worker no-contract, no-paid-leave and no-social-security percentages.
- Table 37: enterprise-size shares and sample total for usual-status employed persons.
- Table 51: manufacturing casual earnings, approximately ₹443 per person-day from 8,771 sampled person-days.
- Table 50: regular-earnings Block 6 mapping and weighting cross-check.
- Table 27 plus its RSE table: Tamil Nadu rural manufacturing share 12.17% and RSE 5.81%.

## Interpretation boundary

PLFS reports worker-side earnings and conditions. ASUSE and ASI report establishment-side compensation. The concepts cannot be linked at the employer-worker level, and differences do not identify a policy or causal effect.
