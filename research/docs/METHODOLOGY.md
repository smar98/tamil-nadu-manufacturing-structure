# Research Method

## Question and estimand

The v1 question is:

> How is Tamil Nadu’s manufacturing employment distributed across establishment sizes and industries, and how do value addition, compensation, worker earnings and job quality compare with India and other manufacturing states?

The current builder covers establishment size, employment composition, establishment-side value addition and compensation, PLFS worker earnings and job quality, and raw plus composition-adjusted peer comparisons. Canonical Layer 5 output replacement and policy interpretation remain later tasks.

The statistical unit is survey-specific. ASUSE observes covered unincorporated establishments, ASI observes sample returns in the registered-factory statistical universe, and PLFS observes people in sampled households. A firm can own multiple establishments, and an ASI return can cover multiple reported units. The output therefore does not treat every record as a firm.

## Survey roles

| Dataset | Statistical unit | Reference period | Role |
| --- | --- | --- | --- |
| ASUSE 2023-24 | Covered unincorporated establishment | Oct 2023-Sep 2024 | Establishment size, workers, industry, GVA and hired-worker emoluments |
| ASI 2023-24 | Sample return; a return can cover multiple reported units | Accounting year 2023-24 | Registered-factory size approximation, persons engaged, GVA, emoluments and labour-cost proxy |
| PLFS 2023-24 | Person in a sampled household; person-day for casual earnings | Jul 2023-Jun 2024 | Worker-side enterprise size, earnings and regular-worker job quality |

The periods overlap but are not identical. Results are a 2023-24 structural comparison, not a synchronized accounting identity.

## Scope and definitions

- Manufacturing is NIC 2008 divisions 10-33.
- **OAE:** ASUSE establishment type 2; no hired worker employed during the major part of the operating period.
- **HWE:** ASUSE establishment type 1; at least one hired worker employed on that basis.
- **ASUSE worker:** working owners, formal and informal hired workers, unpaid family helpers and other reported workers. Counts are people/positions, not full-time equivalents.
- **ASI persons engaged:** Block E row 10, including workers, supervisory and managerial staff, other employees, and unpaid family members/proprietors/cooperative members.
- **ASI paid persons engaged:** Block E rows 6, 7 and 8, equivalently total persons engaged less row 9 unpaid family members/proprietors/cooperative members.
- Common establishment-size bands are 1, 2-4, 5-9, 10-19, 20-49, 50-99, 100-249 and 250+ workers/persons engaged.
- ASI primary size is persons engaged divided by reported units. It is an equal-allocation approximation, not observed unit-level factory size. A separate per-return classification is retained as a sensitivity.

ASUSE, ASI and PLFS remain separate survey universes. Their estimates are not added together or treated as a continuous firm-size distribution.

## Estimation

All estimates use public-use survey multipliers. For an aggregate:

```text
Y_hat = sum_i(weight_i * y_i)
```

Displayed ratios are ratios of weighted totals:

```text
R_hat = sum_i(weight_i * y_i) / sum_i(weight_i * x_i)
```

They are not averages of establishment- or return-level ratios. ASUSE multipliers have two implied decimal places and are divided by 100. ASI multipliers are used directly.

### ASUSE value addition and compensation

- Market-establishment GVA is Level 08 item 769, annualized using Level 03 reference-period fields.
- GVA per worker divides weighted annual GVA by weighted Level 09 item 789 total workers for records with market-establishment GVA.
- Annual emoluments per hired worker uses Level 10 items 902, 903, 912 and 929 over Level 09 items 782 and 783 in HWE establishments.
- Working-owner emolument items 901 and 911 are excluded because working owners are absent from the hired-worker denominator.
- Non-market item 779 is NVA and is not mixed with market-establishment GVA.

### ASI value addition and compensation

- GVA is the existing F-J accounting reconstruction: total output less total input.
- GVA per person engaged divides weighted GVA by weighted Block E row 10.
- Emoluments are wages and salaries plus bonus, divided by paid persons engaged.
- The broader labour-cost proxy adds provident-fund contribution and workmen/staff welfare to emoluments. Welfare is not necessarily cash received by workers, so the proxy is not take-home pay.
- Labour-cost-proxy shares of GVA are reported only for cells with positive aggregate GVA and acceptable GVA concentration.

All monetary results are current rupees. No nominal comparison is described as a real trend; time-series work would require appropriate deflators.

## PLFS enterprise-size cross-check

PLFS usual-status employment combines principal and subsidiary status. An employed principal status takes precedence; otherwise an employed subsidiary status is used. Manufacturing is NIC 10000-33999.

Enterprise-size fields are branch-specific:

- principal: `b5pt1q10_perv1`;
- subsidiary: `b5pt2q9_perv1`.

PLFS is worker-weighted and does not validate ASUSE or ASI establishment counts.

## PLFS worker earnings and job quality

Earnings use current weekly status and the manufacturing industry of the Block 6 earning activity. Three non-comparable measures remain separate: positive regular wage/salaried earnings for the preceding calendar month; non-zero self-employment gross earnings for the last 30 days, including reported losses; and positive casual earnings per qualifying person-day over the previous seven days. The casual measure sums two qualifying manufacturing activities within a day and counts that person-day once. Earnings are not crossed with usual-status enterprise size.

Job-quality rates use the usual-status branch above and are restricted to regular wage/salaried manufacturing workers. Written contract uses codes 2-4 over 1-4; paid leave uses code 1 over 1-2; and specified, no specified, and unknown social security use codes 1-7, 8, and 9 over the common 1-9 denominator. The three social-security rates therefore sum to one. Sex follows the official convention: codes 1 and 3 are male and code 2 is female.

Overall rows cover India and all available States/UTs. Sex and rural/urban rows cover India, Tamil Nadu, Gujarat, Maharashtra, Karnataka, Telangana and Kerala; job quality also has enterprise-size rows for those geographies.

### PLFS design-based uncertainty

For every Layer 4 mean or rate, the builder creates the complete state × sector × NSS region × stratum × rural-sub-stratum design scaffold from the full first-visit person file before applying a domain. Rural sub-stratum is omitted for urban records. Within each design stratum it forms weighted numerator and denominator totals for interpenetrating sub-samples 1 and 2 and applies the official paired-subsample ratio variance. A domain absent from one sub-sample contributes zero rather than deleting that sub-sample. Proportion intervals are clipped to 0-1; lower bounds for positive-only earnings are clipped to zero.

## Layer 5 raw and composition-adjusted peer comparisons

Every Layer 3 and Layer 4 overall outcome compares Tamil Nadu separately with India, Gujarat, Maharashtra, Karnataka, Telangana and Kerala. Raw rows copy the published source estimates exactly. All outcomes report Tamil Nadu minus comparator; rupee outcomes also report the Tamil Nadu/comparator ratio and percentage gap when the comparator estimate is positive. Proportions report only the difference, stored in proportion units for percentage-point display. PLFS source standard errors, RSEs and intervals are copied for each side; no interval or significance test is constructed for a gap.

Adjustment is limited to ASUSE GVA per worker and annual emoluments per hired worker, plus ASI GVA per person engaged, emoluments per paid person engaged and labour-cost proxy per paid person engaged. ASUSE and ASI receive separate seven-group broad-industry and four-group size adjustments. ASI also receives a broad-industry × size adjustment using only the primary equal-allocation size approximation. PLFS adjustment, ASUSE joint adjustment and adjustment of labour-cost-proxy share of GVA are omitted.

Broad cells are built directly from unit records and assessed with the existing Layer 3 outcome-cell rule. A cell is retained only when stable with a positive outcome denominator in both geographies. Retained cells must cover at least 95% of each geography's full eligible denominator, leave at least two common cells, and have positive retained denominator totals. ASI `zero-unclassified` denominator mass is included in the full denominator but not assigned to a common size cell.

Within common support, each geography's denominator weights are renormalised. The common weight for a cell is the average of the Tamil Nadu and comparator weights. The adjusted gap uses those symmetric common weights. The Kitagawa-style composition and within-cell components must satisfy both identities: adjusted gap equals the within component, and the common-support raw gap equals composition plus within. A failed gate remains an explicit suppressed row with coverage diagnostics, null estimate/component fields and no component cells.

Layer 3 has no design-based component-cell variances, so adjusted estimates and decompositions have no confidence intervals or significance tests in v1. The comparisons are descriptive composition controls, not causal effects of industry, size, policy, productivity, formalisation or growth. Pair-specific common weights also mean adjusted comparator rows are not a league table.

## Disclosure and stability

Every public cell reports its unweighted sample count. Structural cells are suppressed when:

- the sample count is below 10; or
- one observation contributes more than 70% of weighted employment.

Value-addition and compensation cells are suppressed when:

- the sample count is below 10; or
- one observation contributes more than 70% of the weighted denominator; or
- one observation contributes more than 70% of the absolute weighted numerator.

Suppressed estimates are `null`, never zero. For size or industry contribution shares, all sibling shares are set to `null` if any sibling is suppressed, preventing recovery of a hidden cell as the residual from one.

Layer 4 uses a separate worker-side rule. It suppresses a mean or rate with fewer than 30 valid positive-weight denominator observations, fewer than 10 active FSUs, Kish effective sample size below 30, more than 20% of denominator weight from one observation, unavailable paired-subsample variance, RSE above 30%, fewer than 10 sampled outcomes or non-outcomes for a rate, or more than 20% of absolute weighted earnings from one person or person-day. Published cells are `stable` at RSE up to 20% and `low_precision` above 20% through 30%. Suppressed estimates, standard errors, RSEs and intervals are `null`. Social-security categories are assessed independently: a rare and unstable unknown category does not suppress the official no-benefit headline or the specified-benefit rate.

The ASUSE GVA-per-worker relative standard error continues to use MoSPI’s Appendix B SRSWR ratio approximation for the legacy reconciliation output; Layer 4 uses the PLFS paired-subsample method above.

## Validation gates

The canonical payload is written only after the legacy ASUSE/PLFS checks and the locked Layer 4 checks pass. Layer 4 reconciles Table 36 India and Tamil Nadu non-agriculture rates, Table 37 all-India non-agriculture enterprise-size shares and sample total, Table 51 manufacturing casual earnings and person-day sample count, and the Tamil Nadu rural manufacturing share and RSE. Percentage checks use half the published rounding unit; integer sample counts match exactly. Layer 5 keeps these 28 published-table gates unchanged and adds focused contract checks for source-row equality, expected row coverage, allowed adjustments, support, weights, decomposition identities, suppression nulls, uncertainty copying and aggregate-only output.

ASI accounting formulas are separately compared with official Tamil Nadu factory-sector totals using a predeclared 5% relative-error gate. The benchmark ledger is stored under `research/derived/`.

## Interpretation boundary

The evidence describes levels and composition within measured survey populations. It cannot establish firm graduation, identify establishments that want to grow, estimate a return to registration, identify a binding growth constraint, or estimate a causal policy effect. Those questions require longitudinal linkage, a valid comparison group, policy-treatment information, or a purpose-built panel.
