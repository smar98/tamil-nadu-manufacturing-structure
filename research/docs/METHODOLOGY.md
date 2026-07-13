# Research Method

## Question and estimand

How do enterprise scale, labor productivity and employment form differ across
Tamil Nadu's own-account manufacturers, unincorporated employers and registered
manufacturing factories in 2023-24?

The estimand is a **cross-sectional structural discontinuity across three
survey-defined populations**. It is not a firm-size distribution over one
common frame, a transition rate, or a causal effect of registration, hiring or
industrial policy.

## Survey roles

| Dataset | Statistical unit | Reference period | Role |
| --- | --- | --- | --- |
| ASUSE 2023-24 | Unincorporated non-agricultural establishment | Oct 2023-Sep 2024 | OAE/HWE structure, workers, GVA and operating characteristics |
| ASI 2023-24 | Factory or other establishment in ASI scope | Accounting year 2023-24 | Registered-sector scale, GVA and workforce structure |
| PLFS 2023-24 | Person in a sampled household | Jul 2023-Jun 2024 | Manufacturing employment share and employment status |

The periods overlap but are not identical. The output is therefore a 2023-24
snapshot rather than a synchronized accounting identity.

## Definitions

- **OAE:** ASUSE establishment type 2; no hired worker employed during the
  major part of the establishment's operating period.
- **HWE:** ASUSE establishment type 1; at least one hired worker employed on
  that basis.
- **ASUSE worker:** payroll workers plus working owners, unpaid family helpers,
  apprentices and interns.
- **ASI registered tier:** status codes 1-3 and NIC 2008 divisions 10-33.
- **ASUSE labor productivity:** annual GVA divided by workers.
- **ASI labor productivity:** annual GVA divided by persons engaged.

The two productivity denominators are close enough for a labeled structural
comparison but are not definitionally identical. "Unincorporated,"
"unregistered," "informal" and "illegal" are not synonyms.

## Estimation

All estimates use public-use survey multipliers. For an aggregate:

```text
Y_hat = sum_i(weight_i * y_i)
```

Displayed ratios are ratios of weighted totals:

```text
R_hat = sum_i(weight_i * y_i) / sum_i(weight_i * x_i)
```

They are not unweighted means of unit-level ratios. ASUSE multipliers are
stored with two implied decimal places and are divided by 100. Reported GVA is
annualized according to each establishment's reference-period code. The
manufacturing domain is NIC 2008 divisions 10-33.

PLFS usual-status employment combines principal and subsidiary status. An
employed principal status takes precedence; otherwise an employed subsidiary
status is used. Manufacturing is NIC 10000-33999.

## Sampling uncertainty

The ASUSE GVA-per-worker relative standard error uses MoSPI's Appendix B
SRSWR ratio approximation. The implementation is accepted only when the
all-activity Tamil Nadu estimate reproduces MoSPI's published 2.64% RSE within
a predeclared 15% relative tolerance.

Sector bubbles require at least 100 sampled establishments in the interface.
That is a display safeguard, not a confidence interval. Sector points are not
ranked and differences are not declared statistically significant.

## Validation gates

The site payload is written only after reconstructing ten published cells:

1. Tamil Nadu manufacturing OAE, HWE and total establishment counts.
2. OAE, HWE and total GVA per worker.
3. PLFS manufacturing worker shares for all, male, female, rural and urban
   workers.
4. The ASUSE all-activity Tamil Nadu GVA-per-worker RSE benchmark.

ASI unit-record formulas are separately compared with official Tamil Nadu
factory-sector totals using a predeclared 5% relative-error gate. The exact
results are stored under `research/derived/`.

## Interpretation boundary

The evidence establishes levels and composition within the measured
populations. It cannot establish firm graduation, an abnormal shortage of
medium firms, a return to registration, a binding growth constraint or a
causal policy effect. A serious transition study requires a governed
longitudinal linkage of administrative records or a purpose-built panel.
