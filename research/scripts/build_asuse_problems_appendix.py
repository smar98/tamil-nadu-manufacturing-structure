#!/usr/bin/env python3
"""Build the ASUSE reported-problems exploratory appendix (Tamil Nadu manufacturing).

Locked spec: research/docs/LAYER6_ASUSE_PROBLEMS_APPENDIX.md.

This is an optional exploratory appendix, not a Layer 3-6 estimand change. It
reads only the raw ASUSE 2023-24 CSV zip and writes an aggregate-only,
disclosure-safe JSON payload. It is deterministic: no wall-clock timestamps,
no random sampling. It never prints or exports respondent-level records or
design identifiers (FSU/PSU/district/dispatch/household/establishment keys).

Universe: Tamil Nadu (state code 33) unincorporated manufacturing
establishments, NIC divisions 10-33, weight = mlt / 100. This mirrors the
filter used in build_manufacturing_structure.py's main(): state == "33" and
major_nic_2dig between 10 and 33.

These are cross-sectional associations, not binding-constraint estimates.
See the interpretation section of the linked doc before citing any number.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
ASUSE_ZIP = RAW / "ASUSE_DATA_2023_24_CSV.zip"
OUTPUT = ROOT / "derived" / "asuse_problems_appendix.json"

TN = "33"
MIN_SAMPLE = 10
MAX_CONCENTRATION = 0.70
# ASUSE 2023-24's reference period ends within calendar 2024; age is computed
# against a single fixed reference year for every establishment. This is an
# approximation (the true reference date varies by unit), documented as such.
AGE_REFERENCE_YEAR = 2024

# Item 225/226 code list ("nature of problems faced by the establishment"),
# research/data/raw/asuse_2023_24_report.txt around line 39797.
PROBLEM_CATEGORIES = [
    {"code": 1, "id": "power", "label": "Erratic power supply / power cuts"},
    {"code": 2, "id": "raw_materials", "label": "Shortage of raw materials"},
    {"code": 3, "id": "market_connectivity", "label": "Lack of connectivity to market due to road or other infrastructure"},
    {"code": 4, "id": "credit_availability_cost", "label": "Non-availability / high cost of credit"},
    {"code": 5, "id": "non_recovery_dues", "label": "Non-recovery of financial dues"},
    {"code": 6, "id": "labour_availability", "label": "Non-availability of labour as and when needed"},
    {"code": 7, "id": "skilled_labour_availability", "label": "Non-availability of skilled labour as and when needed"},
    {"code": 8, "id": "technology_upgrade", "label": "Lack of technological upgrade in the production process"},
    {"code": 9, "id": "other", "label": "Others (specified in remarks)"},
]

SIZE_GROUPS = [
    {"id": "1-9", "label": "1-9 workers", "minimum": 1, "maximum": 9},
    {"id": "10-49", "label": "10-49 workers", "minimum": 10, "maximum": 49},
    {"id": "50-249", "label": "50-249 workers", "minimum": 50, "maximum": 249},
    {"id": "250+", "label": "250+ workers", "minimum": 250, "maximum": None},
]

# Layer 1 published Tamil Nadu manufacturing establishment totals
# (PUBLISHED["asuse"] in build_manufacturing_structure.py).
PUBLISHED_TN_TOTALS = {"oae_establishments": 1_118_993, "hwe_establishments": 272_663}
PUBLISHED_TOLERANCE = 0.01


def zip_member(archive: zipfile.ZipFile, fragment: str) -> str:
    matches = [name for name in archive.namelist() if fragment in name]
    if len(matches) != 1:
        raise ValueError(f"Expected one member containing {fragment!r}; found {matches}")
    return matches[0]


def unit_key(frame: pd.DataFrame, sss_column: str, establishment: str = "sample_est_no") -> pd.Series:
    columns = ["fsu_serial_no", "segment_no", sss_column, establishment]
    return frame[columns].astype("string").fillna("").agg("|".join, axis=1)


def load_frame() -> pd.DataFrame:
    """Assemble the Level 02/03/08/09/12 establishment-level working frame.

    The returned frame never leaves this process as respondent-level output;
    only weighted aggregates derived from it are written to disk.
    """
    with zipfile.ZipFile(ASUSE_ZIP) as archive:
        base = pd.read_csv(archive.open(zip_member(archive, "LEVEL - 02")), low_memory=False)
        reference = pd.read_csv(archive.open(zip_member(archive, "LEVEL - 03")), low_memory=False)
        gva = pd.read_csv(archive.open(zip_member(archive, "LEVEL - 08")), low_memory=False)
        workers = pd.read_csv(archive.open(zip_member(archive, "LEVEL - 09")), low_memory=False)
        loans = pd.read_csv(archive.open(zip_member(archive, "LEVEL - 12")), low_memory=False)

    base["key"] = unit_key(base, "second_stage_stratum_no")
    reference["key"] = unit_key(reference, "second_stage_stratum_no")
    gva["key"] = unit_key(gva, "second_stage_stratum")
    workers["key"] = unit_key(workers, "second_stage_stratum")
    loans["key"] = unit_key(loans, "second_stage_stratum")

    reference = reference[["key", "ref_period_type", "days_closed_govt_order", "months_in_accounting_period"]]
    gva = (
        gva.loc[gva["item_no"].astype(str).eq("769"), ["key", "value_rs"]]
        .rename(columns={"value_rs": "gva_value_rs"})
    )
    total_workers = workers.loc[workers["item_no"].astype(str).eq("789"), ["key", "total_workers"]]
    # Item 1119 is the Block 11 "total (1101 to 1113)" outstanding-loan row.
    # Establishments with no outstanding loan have no row at all in Level 12
    # (sparse long format), so absence means zero, not missing.
    outstanding_loan = (
        loans.loc[loans["item_no"].astype(str).eq("1119"), ["key", "amount_outstanding"]]
        .rename(columns={"amount_outstanding": "loan_outstanding_rs"})
    )

    keep_columns = [
        "key", "nss_region", "major_nic_2dig", "major_nic_5dig", "non_profit",
        "est_type", "mlt", "year_init_operation", "registered", "used_internet",
        "problems_faced", "most_severe_problem", "next_severe_problem",
    ]
    frame = base[keep_columns].merge(reference, on="key", how="left", validate="one_to_one")
    frame = frame.merge(gva, on="key", how="left", validate="one_to_one")
    frame = frame.merge(total_workers, on="key", how="left", validate="one_to_one")
    frame = frame.merge(outstanding_loan, on="key", how="left", validate="one_to_one")
    frame = frame.drop(columns=["key"])

    frame["state"] = (
        pd.to_numeric(frame["nss_region"], errors="coerce")
        .astype("Int64").astype("string").str.zfill(3).str[:2]
    )
    frame["weight"] = frame["mlt"] / 100.0
    frame["annual_factor"] = np.select(
        [
            frame["ref_period_type"].isin([1, 2]),
            frame["ref_period_type"].eq(3),
            frame["ref_period_type"].eq(4),
        ],
        [
            12.0,
            365.0 / (30.0 - frame["days_closed_govt_order"].replace(0, np.nan)),
            12.0 / frame["months_in_accounting_period"].replace(0, np.nan),
        ],
        default=np.nan,
    )
    frame["annual_gva"] = frame["gva_value_rs"] * frame["annual_factor"]
    frame["market"] = frame["non_profit"].ne(1) & frame["major_nic_5dig"].ne(70_100)

    frame["_one"] = 1.0
    frame["has_outstanding_loan"] = frame["loan_outstanding_rs"].fillna(0.0).gt(0.0).astype(float)
    frame["registered_flag"] = frame["registered"].eq(1).astype(float)
    frame["ict_flag"] = frame["used_internet"].eq(1).astype(float)
    age_years = AGE_REFERENCE_YEAR - pd.to_numeric(frame["year_init_operation"], errors="coerce")
    frame["age_years"] = age_years.where(age_years.ge(0))

    for category in PROBLEM_CATEGORIES:
        code = category["code"]
        frame[f"reports_{code}"] = (
            frame["most_severe_problem"].eq(code) | frame["next_severe_problem"].eq(code)
        ).astype(float)

    return frame


def size_group(total_workers: pd.Series) -> pd.Series:
    values = pd.to_numeric(total_workers, errors="coerce")
    choices = [group["id"] for group in SIZE_GROUPS]
    conditions = [
        values.between(1, 9), values.between(10, 49),
        values.between(50, 249), values.ge(250),
    ]
    return pd.Series(np.select(conditions, choices, default=None), index=values.index, dtype="string")


def weighted_cell(group: pd.DataFrame, numerator: str, denominator: str) -> dict:
    """Weighted ratio of totals, with the Layer 3 outcome-cell disclosure rule.

    Suppress when unweighted sample count < 10, or one observation
    contributes > 70% of the weighted denominator, or > 70% of the absolute
    weighted numerator. Suppressed values are null, never zero.
    """
    weight = group["weight"].clip(lower=0.0)
    numerator_values = weight * group[numerator].astype(float)
    denominator_values = weight * group[denominator].astype(float)
    denominator_total = float(denominator_values.sum())
    numerator_total = float(numerator_values.sum())
    absolute_numerator = numerator_values.abs()
    absolute_numerator_total = float(absolute_numerator.sum())
    sample_count = int(len(group))

    denominator_concentration = (
        float(denominator_values.max() / denominator_total) if denominator_total > 0 else 0.0
    )
    numerator_concentration = (
        float(absolute_numerator.max() / absolute_numerator_total) if absolute_numerator_total > 0 else 0.0
    )

    reasons = []
    if sample_count < MIN_SAMPLE:
        reasons.append(f"sample count below {MIN_SAMPLE}")
    if denominator_total <= 0:
        reasons.append("non-positive weighted denominator")
    if denominator_concentration > MAX_CONCENTRATION:
        reasons.append(f"largest weighted-denominator contribution exceeds {MAX_CONCENTRATION:.0%}")
    if numerator_concentration > MAX_CONCENTRATION:
        reasons.append(f"largest absolute weighted-numerator contribution exceeds {MAX_CONCENTRATION:.0%}")

    stable = not reasons
    return {
        "sample_count": sample_count,
        "value": (numerator_total / denominator_total) if stable else None,
        "stability": "stable" if stable else "suppressed",
        "suppression_reason": None if stable else "; ".join(reasons),
    }


def null_suppressed_sibling(reporter_cell: dict, non_reporter_cell: dict) -> None:
    """Null both sides of a reporter/non-reporter pair if either is suppressed.

    Reporters and non-reporters always sum to the same fixed universe total
    for a given outcome, and that universe total is public elsewhere in this
    project (e.g. Layer 3's Tamil Nadu GVA-per-worker figure). Publishing one
    stable side plus the known total would let a reader back out a suppressed
    sibling by subtraction, so both sides are nulled together.
    """
    if reporter_cell["stability"] == "suppressed" or non_reporter_cell["stability"] == "suppressed":
        for cell in (reporter_cell, non_reporter_cell):
            if cell["stability"] != "suppressed":
                cell["stability"] = "suppressed"
                cell["suppression_reason"] = "nulled to prevent residual reconstruction of a suppressed sibling cell"
                cell["value"] = None


def build_reporting_shares(domain: pd.DataFrame) -> list[dict]:
    """Deliverable 1: weighted share reporting each problem, by breakdown."""
    rows = []
    est_type_groups = [(1, "hwe", "Hired-worker enterprise"), (2, "oae", "Own-account enterprise")]
    size_ids = size_group(domain["total_workers"])

    for category in PROBLEM_CATEGORIES:
        flag_column = f"reports_{category['code']}"

        overall = weighted_cell(domain, flag_column, "_one")
        rows.append({
            "category_code": category["code"], "category_id": category["id"],
            "category_label": category["label"], "dimension": "overall",
            "group_id": "all", "group_label": "All manufacturing establishments",
            **overall,
        })

        for est_code, group_id, group_label in est_type_groups:
            group = domain.loc[domain["est_type"].eq(est_code)]
            rows.append({
                "category_code": category["code"], "category_id": category["id"],
                "category_label": category["label"], "dimension": "establishment_type",
                "group_id": group_id, "group_label": group_label,
                **weighted_cell(group, flag_column, "_one"),
            })

        for size in SIZE_GROUPS:
            group = domain.loc[size_ids.eq(size["id"])]
            rows.append({
                "category_code": category["code"], "category_id": category["id"],
                "category_label": category["label"], "dimension": "size_group",
                "group_id": size["id"], "group_label": size["label"],
                **weighted_cell(group, flag_column, "_one"),
            })
    return rows


def build_gva_by_reporting(domain: pd.DataFrame) -> list[dict]:
    """Deliverable 2: weighted GVA per worker, reporters vs non-reporters.

    Market establishments with valid (non-null) GVA only, matching the Layer
    3 value-addition definition (research/docs/LAYER3_FIELD_MAP.md).
    """
    gva_domain = domain.loc[domain["market"] & domain["annual_gva"].notna()]
    rows = []
    for category in PROBLEM_CATEGORIES:
        flag_column = f"reports_{category['code']}"
        reporters = gva_domain.loc[gva_domain[flag_column].eq(1.0)]
        non_reporters = gva_domain.loc[gva_domain[flag_column].eq(0.0)]

        reporter_cell = weighted_cell(reporters, "annual_gva", "total_workers")
        non_reporter_cell = weighted_cell(non_reporters, "annual_gva", "total_workers")
        null_suppressed_sibling(reporter_cell, non_reporter_cell)

        rows.append({
            "category_code": category["code"], "category_id": category["id"],
            "category_label": category["label"], "reporting": True,
            **reporter_cell,
        })
        rows.append({
            "category_code": category["code"], "category_id": category["id"],
            "category_label": category["label"], "reporting": False,
            **non_reporter_cell,
        })
    return rows


CORRELATE_METRICS = [
    {"id": "registration_share", "label": "Share with any registration", "numerator": "registered_flag", "denominator": "_one"},
    {"id": "ict_share", "label": "Share using ICT / internet", "numerator": "ict_flag", "denominator": "_one"},
    {"id": "loan_share", "label": "Share with an outstanding loan", "numerator": "has_outstanding_loan", "denominator": "_one"},
    {"id": "mean_age_years", "label": "Weighted mean establishment age (years)", "numerator": "age_years", "denominator": "_one", "requires_age": True},
]


def build_correlates_by_reporting(domain: pd.DataFrame) -> list[dict]:
    """Deliverable 3: registration / ICT / loan / age, reporters vs non-reporters."""
    rows = []
    for category in PROBLEM_CATEGORIES:
        flag_column = f"reports_{category['code']}"
        for metric in CORRELATE_METRICS:
            base = domain.loc[domain["age_years"].notna()] if metric.get("requires_age") else domain
            reporters = base.loc[base[flag_column].eq(1.0)]
            non_reporters = base.loc[base[flag_column].eq(0.0)]

            reporter_cell = weighted_cell(reporters, metric["numerator"], metric["denominator"])
            non_reporter_cell = weighted_cell(non_reporters, metric["numerator"], metric["denominator"])
            null_suppressed_sibling(reporter_cell, non_reporter_cell)

            rows.append({
                "category_code": category["code"], "category_id": category["id"],
                "category_label": category["label"], "metric_id": metric["id"],
                "metric_label": metric["label"], "reporting": True,
                **reporter_cell,
            })
            rows.append({
                "category_code": category["code"], "category_id": category["id"],
                "category_label": category["label"], "metric_id": metric["id"],
                "metric_label": metric["label"], "reporting": False,
                **non_reporter_cell,
            })
    return rows


BANNED_SUBSTRINGS = [
    "fsu_serial_no", "sample_est_no", "second_stage_stratum", "district",
    "dispatch", "household", "psu", "dsl", "nss_region",
]


def self_check(domain: pd.DataFrame, payload: dict) -> None:
    oae_total = float(domain.loc[domain["est_type"].eq(2), "weight"].sum())
    hwe_total = float(domain.loc[domain["est_type"].eq(1), "weight"].sum())

    def within_tolerance(estimate: float, published: float) -> bool:
        return abs(estimate - published) / published <= PUBLISHED_TOLERANCE

    assert within_tolerance(oae_total, PUBLISHED_TN_TOTALS["oae_establishments"]), (
        f"OAE weight sum {oae_total:,.0f} is outside {PUBLISHED_TOLERANCE:.0%} of the published "
        f"{PUBLISHED_TN_TOTALS['oae_establishments']:,}"
    )
    assert within_tolerance(hwe_total, PUBLISHED_TN_TOTALS["hwe_establishments"]), (
        f"HWE weight sum {hwe_total:,.0f} is outside {PUBLISHED_TOLERANCE:.0%} of the published "
        f"{PUBLISHED_TN_TOTALS['hwe_establishments']:,}"
    )

    all_rows = (
        payload["reporting_shares"] + payload["gva_per_worker_by_reporting"]
        + payload["correlates_by_reporting"]
    )
    for row in all_rows:
        if row["stability"] == "stable":
            assert row["value"] is not None, f"Stable row published a null value: {row}"
            assert row["sample_count"] >= MIN_SAMPLE, f"Stable row below minimum sample size: {row}"
        else:
            assert row["value"] is None, f"Suppressed row leaked a non-null value: {row}"
            assert row["suppression_reason"], f"Suppressed row missing a reason: {row}"

    def sibling_pairs(rows: list[dict], key_fields: tuple[str, ...]) -> dict[tuple, list[dict]]:
        groups: dict[tuple, list[dict]] = {}
        for row in rows:
            key = tuple(row[field] for field in key_fields)
            groups.setdefault(key, []).append(row)
        return groups

    for rows, key_fields in [
        (payload["gva_per_worker_by_reporting"], ("category_code",)),
        (payload["correlates_by_reporting"], ("category_code", "metric_id")),
    ]:
        for pair in sibling_pairs(rows, key_fields).values():
            assert len(pair) == 2, f"Expected exactly one reporter/non-reporter pair, found {pair}"
            stabilities = {row["stability"] for row in pair}
            assert stabilities != {"stable", "suppressed"}, (
                f"Sibling pair has one stable and one suppressed cell, residual reconstruction risk: {pair}"
            )

    dumped = json.dumps(payload)
    lowered = dumped.lower()
    for banned in BANNED_SUBSTRINGS:
        assert banned not in lowered, f"Banned identifier fragment {banned!r} found in output payload"


def main() -> int:
    frame = load_frame()
    domain = frame.loc[frame["state"].eq(TN) & frame["major_nic_2dig"].between(10, 33)].copy()

    reporting_shares = build_reporting_shares(domain)
    gva_by_reporting = build_gva_by_reporting(domain)
    correlates_by_reporting = build_correlates_by_reporting(domain)

    payload = {
        "metadata": {
            "title": "ASUSE 2023-24 reported-problems exploratory appendix, Tamil Nadu manufacturing",
            "status": "exploratory, hypothesis-generating correlations; not binding-constraint estimates",
            "universe": "Tamil Nadu unincorporated manufacturing establishments, NIC divisions 10-33, ASUSE 2023-24",
            "weight": "mlt / 100",
            "endogeneity_caveat": (
                "These are cross-sectional associations only. Reverse causation and selection are "
                "plausible: for example, more productive establishments may seek more finance, so a "
                "positive association between reporting a credit problem and higher GVA per worker "
                "would not imply that credit access constrains growth. The permitted wording is "
                "'establishments reporting X differ on Y', never 'X constrains growth'."
            ),
            "disclosure_rule": (
                "Suppress when unweighted sample count < 10, or one observation contributes > 70% of "
                "the weighted denominator, or > 70% of the absolute weighted numerator. Suppressed "
                "values are null, never zero. Every published cell carries its unweighted sample "
                "count. Reporter/non-reporter sibling pairs are nulled together if either side would "
                "otherwise be suppressed."
            ),
            "field_map_doc": "research/docs/LAYER6_ASUSE_PROBLEMS_APPENDIX.md",
        },
        "problem_categories": PROBLEM_CATEGORIES,
        "size_groups": SIZE_GROUPS,
        "reporting_shares": reporting_shares,
        "gva_per_worker_by_reporting": gva_by_reporting,
        "correlates_by_reporting": correlates_by_reporting,
    }

    self_check(domain, payload)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w") as handle:
        json.dump(payload, handle, indent=2)

    stable_shares = sum(1 for row in reporting_shares if row["stability"] == "stable")
    stable_gva = sum(1 for row in gva_by_reporting if row["stability"] == "stable")
    stable_correlates = sum(1 for row in correlates_by_reporting if row["stability"] == "stable")
    print(
        "Wrote", OUTPUT, "with",
        f"{len(reporting_shares)} reporting-share rows ({stable_shares} stable),",
        f"{len(gva_by_reporting)} GVA-per-worker rows ({stable_gva} stable),",
        f"{len(correlates_by_reporting)} correlate rows ({stable_correlates} stable).",
        "All self-checks passed.",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
