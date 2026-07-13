# ASUSE design-based uncertainty — locked method (Layer 3 addendum)

## RESOLUTION 2026-07-13: addendum withdrawn — exact replication infeasible from public files

The implementation stopped at the validation gates, as this file required. Diagnosis
(verified evidence in the session scratchpad `diag/` outputs): with the estimation universe
aligned to the published tables exactly — all seven gate cells match the published sample
counts precisely, and the Table 46 establishment total reproduces the published 4,524,484 to
the rupee — the Appendix B §6 formula still misses the published RSEs by −0.70 to +4.74
points **in inconsistent directions** (TN rural too low; TN urban, Gujarat and all-India too
high; both count RSEs far too low). Sign-flipping errors cannot come from a universe rule.
Out-of-coverage exclusion was ruled out (Level 02 already contains only within-coverage
units). Zero-variance strata are immaterial (≤0.11% of the denominator). The remaining
explanation is that MoSPI's official RSEs use listing-schedule (LSU) design information not
present in the public ESU unit files — in particular the true per-stratum surveyed-FSU
counts, where surveyed FSUs containing zero within-coverage establishments are invisible in
the public data yet raise official variances.

**Supervisor decision:** do not publish project-computed ASUSE standard errors (an
approximation that reads 9.4% where MoSPI publishes 4.65% would misinform). Instead: (a) the
site and paper cite MoSPI's published RSE tables (Tables 46–49) as the uncertainty context
for establishment-side estimates — e.g. published all-activities GVA-per-worker RSEs of 2.64%
(TN), 4.65% (Gujarat), 1.12% (India), with manufacturing-specific cells necessarily somewhat
less precise; (b) the methods document the replication attempt and its result as a
demonstrated limitation of the public-use files; (c) Layer 3/5 estimates remain published
without intervals, as the original locked decision stated. No payload change was made; the
canonical payload is untouched. Obtaining LSU data from MoSPI would reopen this addendum.

The specification below is retained for the record and for a future LSU-enabled attempt.

---

Locked 2026-07-13 for paper-grade uncertainty on ASUSE establishment-side estimates. This is
an **additive** amendment: no point estimate, stability label, suppression decision, Layer 5
retained-cell set, gate or interpretation may change.

## Estimator (MoSPI ASUSE 2023-24 Appendix B, section 6)

ASUSE sampling is SRSWOR treated as SRSWR (official approximation; sampling fraction is
small). For stratum st (= sector × NSS region × stratum × sub-stratum), FSU i:

```text
Var(Y_hat) = sum_st [ 1/(n_st(n_st-1)) * sum_i (n_st*Y_hat_sti - Y_hat_st)^2 ]

MSE(R_hat) = (1/X_hat^2) * sum_st [ 1/(n_st(n_st-1))
             * sum_i ( n_st*(Y_hat_sti - R_hat*X_hat_sti) - (Y_hat_st - R_hat*X_hat_st) )^2 ]
```

where Y_hat_sti is the multiplier-weighted FSU total (the multiplier already carries
N_st/n_st, so multiplying the FSU weighted total by n_st matches the N_st*Y_sti notation),
Y_hat_st sums FSU totals in the stratum, and n_st counts sampled FSUs in the stratum.
Domain estimation by zero-fill: unsampled-domain units contribute zero inside their FSU;
FSUs and strata are never dropped for having no domain units. Strata with n_st < 2
contribute zero variance (document the affected weight share). RSE = 100*sqrt(MSE)/|R_hat|;
ci95 = estimate ± 1.96*sqrt(MSE), lower bound clipped at zero for positive-only quantities.

**Universe correction (suspected cause of the current 2.85 vs published 2.64):** official
RSEs are "based on all the surveyed units excluding the out of coverage" (report §3.10.1).
The implementation must identify the survey-status/coverage code in the unit files and
exclude out-of-coverage units from the variance universe exactly as from estimation. If the
existing legacy `ratio_rse` disagrees with the published tables beyond tolerance, diagnose
against this exclusion first; do not tune anything else to force agreement.

## Validation gates (hard; from published report Tables 46-48, all-activities, market rules as each table states)

| Target | Published |
|---|---|
| Table 48 GVA/worker RSE, Tamil Nadu rural / urban / combined | 3.41 / 3.21 / 2.64 |
| Table 48 GVA/worker RSE, Gujarat combined | 4.65 |
| Table 48 GVA/worker RSE, all-India combined | 1.12 |
| Table 46 estimated-establishments RSE, Tamil Nadu combined | extract from report and gate |
| Table 47 estimated-workers RSE, Tamil Nadu combined | extract from report and gate |

Tolerance: absolute difference ≤ 0.10 RSE points per gated cell. If unattainable, stop and
return the diagnosis to the supervisor — do not loosen the tolerance or redefine the target.
The legacy `uncertainty` payload block must be recomputed with the corrected universe and its
values updated (its method string already cites Appendix B §6).

## Payload changes (all additive)

1. `structure_v1.value_addition` and `structure_v1.establishment_compensation` ASUSE rows
   (every dimension: overall, size, nic2): add `standard_error`, `rse`, `ci95_lower`,
   `ci95_upper`. RSE stored as a proportion (consistent with Layer 4 rows). Suppressed rows:
   all four fields null. ASI rows: fields present and null (no design information is
   published for ASI; keep the documented limitation).
2. `structure_v1.peer_comparisons_raw` ASUSE rows: copy each side's new standard error, RSE
   and interval exactly as the PLFS rows already do. No gap interval (unchanged rule).
3. `structure_v1.peer_comparisons_adjusted` ASUSE rows: each `components` entry gains
   `tn_cell_rate_se` and `comparator_cell_rate_se` (null when not computable). Row-level
   `uncertainty_available` stays `false`; update `metadata.layer5.uncertainty_note` to state
   that ASUSE component-cell standard errors are published, but no row-level interval is
   constructed because covariance from the estimated common weights is not modelled. The
   locked no-row-CI decision stands; this publishes the ingredients only.
4. `structure_v1.metadata.layer3`: add an `uncertainty` note naming the Appendix B method,
   the out-of-coverage exclusion, the zero-variance-strata share, and the ASI limitation.

## Boundaries

- Point estimates, stability labels, suppression, Layer 5 gates and retained cells must be
  byte-identical in behaviour: verify by comparing every pre-existing field of the new
  payload against the current canonical payload (only added fields and the two metadata
  notes may differ, plus the corrected legacy `uncertainty` block).
- All 28 published-table gates plus the new RSE gates must pass. Tests: extend the Layer 3
  contract test for the new fields; the Layer 5 contract test's `uncertainty_available ===
  false` assertion stays.
- Scratch build first; canonical replacement only after the full suite passes.
- Public and research payloads stay byte-identical. No frontend change in this chunk.
