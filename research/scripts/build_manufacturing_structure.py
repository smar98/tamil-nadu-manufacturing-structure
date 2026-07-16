#!/usr/bin/env python3
"""Build the Tamil Nadu manufacturing structure dataset.

The script keeps restricted public-use records local and exports only weighted,
disclosure-safe aggregates. It also fails when unit-level reconstructions drift
materially from MoSPI's published tables.
"""

from __future__ import annotations

import json
import math
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from build_asi_aggregates import (
    build_factory_frame,
    dsl_column,
    employment_values,
    numeric,
    pick_column,
    read_block,
    string_values,
)


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "derived"
SITE_DATA = ROOT.parent / "public" / "data" / "manufacturing-structure.json"
ASUSE_ZIP = RAW / "ASUSE_DATA_2023_24_CSV.zip"
PLFS_ZIP = RAW / "CSV_data_PLFS_2023_2024.zip"
ASI_PANEL = PROCESSED / "asi_aggregates.csv"
ASI_2023_ZIP = RAW / "asi" / "ASI_DATA_2023_24_CSV.zip"

TN = "33"
PLFS_EMPLOYED_STATUSES = {11, 12, 21, 31, 41, 51}
PLFS_REGULAR_STATUSES = {31, 71, 72}
PLFS_SELF_EMPLOYED_STATUSES = {11, 12, 61, 62}
PLFS_CASUAL_STATUSES = {41, 42, 51}
SURVEYS = {"asuse", "asi", "plfs"}
STABILITY = {"stable", "low_precision", "suppressed"}
MIN_SAMPLE = 10
MAX_EMPLOYMENT_CONCENTRATION = 0.70
PLFS_MIN_SAMPLE = 30
PLFS_MIN_ACTIVE_FSUS = 10
PLFS_MIN_EFFECTIVE_N = 30
PLFS_MAX_WEIGHT_SHARE = 0.20
PLFS_MAX_OUTCOME_SHARE = 0.20
PLFS_STABLE_RSE = 0.20
PLFS_MAX_RSE = 0.30
PLFS_MIN_BINARY_OUTCOMES = 10

SIZE_BANDS = [
    {"id": "1", "label": "1", "minimum": 1, "maximum": 1},
    {"id": "2-4", "label": "2-4", "minimum": 2, "maximum": 4},
    {"id": "5-9", "label": "5-9", "minimum": 5, "maximum": 9},
    {"id": "10-19", "label": "10-19", "minimum": 10, "maximum": 19},
    {"id": "20-49", "label": "20-49", "minimum": 20, "maximum": 49},
    {"id": "50-99", "label": "50-99", "minimum": 50, "maximum": 99},
    {"id": "100-249", "label": "100-249", "minimum": 100, "maximum": 249},
    {"id": "250+", "label": "250+", "minimum": 250, "maximum": None},
]
MIDDLE_DEFINITIONS = [
    {"id": "10-249", "label": "10-249 workers", "size_bands": ["10-19", "20-49", "50-99", "100-249"]},
    {"id": "10-99", "label": "10-99 workers", "size_bands": ["10-19", "20-49", "50-99"]},
    {"id": "20-249", "label": "20-249 workers", "size_bands": ["20-49", "50-99", "100-249"]},
    {"id": "50-249", "label": "50-249 workers", "size_bands": ["50-99", "100-249"]},
]
STATE_LABELS = {
    "01": "Jammu & Kashmir", "02": "Himachal Pradesh", "03": "Punjab",
    "04": "Chandigarh", "05": "Uttarakhand", "06": "Haryana", "07": "Delhi",
    "08": "Rajasthan", "09": "Uttar Pradesh", "10": "Bihar", "11": "Sikkim",
    "12": "Arunachal Pradesh", "13": "Nagaland", "14": "Manipur", "15": "Mizoram",
    "16": "Tripura", "17": "Meghalaya", "18": "Assam", "19": "West Bengal",
    "20": "Jharkhand", "21": "Odisha", "22": "Chhattisgarh", "23": "Madhya Pradesh",
    "24": "Gujarat", "25": "Dadra & Nagar Haveli and Daman & Diu",
    "27": "Maharashtra", "28": "Andhra Pradesh", "29": "Karnataka", "30": "Goa",
    "31": "Lakshadweep", "32": "Kerala", "33": "Tamil Nadu", "34": "Puducherry",
    "35": "Andaman & Nicobar Islands", "36": "Telangana", "37": "Ladakh",
}
PEER_CODES = ["24", "27", "29", "36"]
SENSITIVITY_CODES = ["32"]
LAYER5_COMPARATORS = [
    {"id": "IN", "label": "India", "type": "country"},
    *[
        {"id": code, "label": STATE_LABELS[code], "type": "core_peer"}
        for code in PEER_CODES
    ],
    *[
        {"id": code, "label": STATE_LABELS[code], "type": "sensitivity"}
        for code in SENSITIVITY_CODES
    ],
]
LAYER5_MIN_COVERAGE = 0.95

NIC2 = {
    10: "Food products", 11: "Beverages", 12: "Tobacco", 13: "Textiles",
    14: "Apparel", 15: "Leather & footwear", 16: "Wood products",
    17: "Paper", 18: "Printing", 19: "Coke & refined petroleum",
    20: "Chemicals", 21: "Pharmaceuticals", 22: "Rubber & plastics",
    23: "Non-metallic minerals", 24: "Basic metals",
    25: "Fabricated metals", 26: "Electronics", 27: "Electrical equipment",
    28: "Machinery", 29: "Motor vehicles", 30: "Other transport",
    31: "Furniture", 32: "Other manufacturing", 33: "Repair & installation",
}
LAYER5_INDUSTRY_GROUPS = [
    {"id": "food_beverage_tobacco", "label": "Food, beverages and tobacco", "nic2": [10, 11, 12]},
    {"id": "textiles_apparel_leather", "label": "Textiles, apparel and leather", "nic2": [13, 14, 15]},
    {"id": "wood_paper_printing_other_repair", "label": "Wood, paper, printing, other manufacturing and repair", "nic2": [16, 17, 18, 31, 32, 33]},
    {"id": "chemicals_petroleum_pharma_rubber", "label": "Petroleum, chemicals, pharmaceuticals and rubber/plastics", "nic2": [19, 20, 21, 22]},
    {"id": "minerals_metals", "label": "Non-metallic minerals and metals", "nic2": [23, 24, 25]},
    {"id": "machinery_electrical_electronics", "label": "Computers, electrical equipment and machinery", "nic2": [26, 27, 28]},
    {"id": "transport_equipment", "label": "Motor vehicles and other transport equipment", "nic2": [29, 30]},
]
LAYER5_SIZE_GROUPS = [
    {"id": "1-9", "label": "1-9 workers", "size_bands": ["1", "2-4", "5-9"]},
    {"id": "10-49", "label": "10-49 workers", "size_bands": ["10-19", "20-49"]},
    {"id": "50-249", "label": "50-249 workers", "size_bands": ["50-99", "100-249"]},
    {"id": "250+", "label": "250+ workers", "size_bands": ["250+"]},
]
LAYER5_RAW_OUTCOMES = [
    {"survey": "asuse", "source": "value_addition", "outcome": "gva_per_worker", "label": "GVA per worker in market establishments", "family": "value_addition", "unit": "current rupees per worker per year", "value_field": "per_person_value"},
    {"survey": "asuse", "source": "establishment_compensation", "outcome": "annual_emoluments_per_hired_worker", "label": "Annual emoluments per hired worker", "family": "compensation", "unit": "current rupees per hired worker per year", "value_field": "per_person_value", "concept": "annual_emoluments"},
    {"survey": "asi", "source": "value_addition", "outcome": "gva_per_person_engaged", "label": "GVA per person engaged", "family": "value_addition", "unit": "current rupees per person engaged per year", "value_field": "per_person_value"},
    {"survey": "asi", "source": "establishment_compensation", "outcome": "emoluments_per_paid_person_engaged", "label": "Emoluments per paid person engaged", "family": "compensation", "unit": "current rupees per paid person engaged per year", "value_field": "per_person_value", "concept": "emoluments"},
    {"survey": "asi", "source": "establishment_compensation", "outcome": "labour_cost_proxy_per_paid_person_engaged", "label": "Labour-cost proxy per paid person engaged", "family": "compensation", "unit": "current rupees per paid person engaged per year", "value_field": "per_person_value", "concept": "labour_cost_proxy"},
    {"survey": "asi", "source": "establishment_compensation", "outcome": "labour_cost_proxy_share_of_gva", "label": "Labour-cost proxy share of GVA", "family": "compensation", "unit": "proportion", "value_field": "labour_cost_proxy_share_of_gva", "concept": "labour_cost_proxy", "is_proportion": True},
    {"survey": "plfs", "source": "worker_earnings", "outcome": "regular_monthly_earnings", "label": "Monthly regular wage/salaried earnings", "family": "earnings", "unit": "rupees per month", "value_field": "estimate", "concept": "regular_monthly_earnings"},
    {"survey": "plfs", "source": "worker_earnings", "outcome": "self_employment_30_day_gross_earnings", "label": "Gross self-employment earnings in the last 30 days", "family": "earnings", "unit": "rupees per 30 days (gross)", "value_field": "estimate", "concept": "self_employment_30_day_gross_earnings"},
    {"survey": "plfs", "source": "worker_earnings", "outcome": "casual_person_day_earnings", "label": "Casual earnings per person-day", "family": "earnings", "unit": "rupees per person-day", "value_field": "estimate", "concept": "casual_person_day_earnings"},
    {"survey": "plfs", "source": "worker_job_quality", "outcome": "written_contract", "label": "Has a written job contract", "family": "job_quality", "unit": "proportion", "value_field": "estimate", "concept": "written_contract", "is_proportion": True},
    {"survey": "plfs", "source": "worker_job_quality", "outcome": "paid_leave", "label": "Eligible for paid leave", "family": "job_quality", "unit": "proportion", "value_field": "estimate", "concept": "paid_leave", "is_proportion": True},
    {"survey": "plfs", "source": "worker_job_quality", "outcome": "specified_social_security", "label": "Eligible for a specified social-security benefit", "family": "job_quality", "unit": "proportion", "value_field": "estimate", "concept": "specified_social_security", "is_proportion": True},
    {"survey": "plfs", "source": "worker_job_quality", "outcome": "no_social_security", "label": "Not eligible for a specified social-security benefit", "family": "job_quality", "unit": "proportion", "value_field": "estimate", "concept": "no_social_security", "is_proportion": True},
]
LAYER5_ADJUSTMENT_OUTCOMES = [
    {"survey": "asuse", "outcome": "gva_per_worker", "label": "GVA per worker in market establishments", "unit": "current rupees per worker per year", "numerator": "annual_gva", "denominator": "total_workers", "dimensions": ["industry", "size"]},
    {"survey": "asuse", "outcome": "annual_emoluments_per_hired_worker", "label": "Annual emoluments per hired worker", "unit": "current rupees per hired worker per year", "numerator": "annual_emoluments", "denominator": "hired_workers", "dimensions": ["industry", "size"]},
    {"survey": "asi", "outcome": "gva_per_person_engaged", "label": "GVA per person engaged", "unit": "current rupees per person engaged per year", "numerator": "gva", "denominator": "employees", "dimensions": ["industry", "size", "industry_size"]},
    {"survey": "asi", "outcome": "emoluments_per_paid_person_engaged", "label": "Emoluments per paid person engaged", "unit": "current rupees per paid person engaged per year", "numerator": "emoluments", "denominator": "paid_persons_engaged", "dimensions": ["industry", "size", "industry_size"]},
    {"survey": "asi", "outcome": "labour_cost_proxy_per_paid_person_engaged", "label": "Labour-cost proxy per paid person engaged", "unit": "current rupees per paid person engaged per year", "numerator": "compensation_employees", "denominator": "paid_persons_engaged", "dimensions": ["industry", "size", "industry_size"]},
]

PUBLISHED = {
    "asuse": {
        "oae_establishments": 1_118_993,
        "hwe_establishments": 272_663,
        "all_establishments": 1_391_656,
        "oae_productivity": 75_693,
        "hwe_productivity": 187_330,
        "all_productivity": 132_755,
        "all_workers": 2_791_450,
        "hired_workers": 1_078_944,
        "annual_emoluments_per_hired_worker": 140_133,
        "source": "ASUSE 2023-24 full report, Tables 5, 30, 34 and 36",
    },
    "plfs": {
        "manufacturing_share": 15.97,
        "male_manufacturing_share": 16.30,
        "female_manufacturing_share": 15.44,
        "rural_manufacturing_share": 12.17,
        "urban_manufacturing_share": 21.73,
        "rural_manufacturing_rse": 5.81,
        "table36": {
            "IN": {"no_written_contract": 0.580, "no_paid_leave": 0.473, "no_social_security": 0.534},
            "33": {"no_written_contract": 0.504, "no_paid_leave": 0.414, "no_social_security": 0.480},
        },
        "table37": {
            "shares": {1: 0.633, 2: 0.109, 3: 0.065, 4: 0.185, 9: 0.008},
            "sample_total": 110_937,
        },
        "table51": {"manufacturing_casual_earnings": 443, "sample_person_days": 8_771},
        "source": "PLFS 2023-24 annual report, Tables 27, 36, 37 and 51 and the Table 27 RSE table",
    },
}


def plfs_daily_activity_fields(day: int) -> tuple[tuple[str, str, str], tuple[str, str, str]]:
    first_status = f"b6q4_3pt{day}" if day == 2 else f"b6q4_3pt{day}_perv1"
    first_industry = f"b6q5_3pt{day}" if day in {2, 7} else f"b6q5_3pt{day}_perv1"
    second_status = (
        "b6q4_act2_3pt5_act2_perv1" if day == 5 else f"b6q4_act2_3pt{day}_perv1"
    )
    return (
        (first_status, first_industry, f"b6q9_3pt{day}_perv1"),
        (second_status, f"b6q5_act2_3pt{day}_perv1", f"b6q9_act2_3pt{day}_perv1"),
    )


def zip_member(archive: zipfile.ZipFile, fragment: str) -> str:
    matches = [name for name in archive.namelist() if fragment in name]
    if len(matches) != 1:
        raise ValueError(f"Expected one member containing {fragment!r}; found {matches}")
    return matches[0]


def unit_key(frame: pd.DataFrame, sss: str, establishment: str = "sample_est_no") -> pd.Series:
    columns = ["fsu_serial_no", "segment_no", sss, establishment]
    return frame[columns].astype("string").fillna("").agg("|".join, axis=1)


def weighted_ratio(frame: pd.DataFrame, numerator: str, denominator: str) -> float:
    top = (frame[numerator] * frame["weight"]).sum()
    bottom = (frame[denominator] * frame["weight"]).sum()
    return float(top / bottom) if bottom else math.nan


def weighted_share(frame: pd.DataFrame, condition: pd.Series) -> float:
    denominator = frame["weight"].sum()
    return float((condition.astype(float) * frame["weight"]).sum() / denominator) if denominator else math.nan


def asuse_frame() -> pd.DataFrame:
    with zipfile.ZipFile(ASUSE_ZIP) as archive:
        base = pd.read_csv(archive.open(zip_member(archive, "LEVEL - 02")), low_memory=False)
        reference = pd.read_csv(archive.open(zip_member(archive, "LEVEL - 03")), low_memory=False)
        gva = pd.read_csv(archive.open(zip_member(archive, "LEVEL - 08")), low_memory=False)
        workers = pd.read_csv(archive.open(zip_member(archive, "LEVEL - 09")), low_memory=False)
        emoluments = pd.read_csv(archive.open(zip_member(archive, "LEVEL - 10")), low_memory=False)

    base["key"] = unit_key(base, "second_stage_stratum_no")
    reference["key"] = unit_key(reference, "second_stage_stratum_no")
    gva["key"] = unit_key(gva, "second_stage_stratum")
    workers["key"] = unit_key(workers, "second_stage_stratum")
    emoluments["key"] = unit_key(emoluments, "second_stage_stratum")

    reference = reference[[
        "key", "ref_period_type", "days_closed_govt_order", "months_in_accounting_period"
    ]]
    gva = (
        gva.loc[gva["item_no"].astype(str).eq("769"), ["key", "value_rs"]]
        .rename(columns={"value_rs": "gva_value_rs"})
    )
    total_workers = workers.loc[workers["item_no"].astype(str).eq("789"), [
        "key", "full_time_male", "full_time_female", "full_time_trans",
        "part_time_male", "part_time_female", "part_time_trans", "total_workers",
    ]]
    hired_workers = (
        workers.loc[workers["item_no"].astype(str).isin(["782", "783"]), ["key", "item_no", "total_workers"]]
        .assign(item_no=lambda data: data["item_no"].astype(str).map({"782": "formal_hired_workers", "783": "informal_hired_workers"}))
        .pivot(index="key", columns="item_no", values="total_workers")
        .reset_index()
    )
    emoluments = (
        emoluments.loc[
            emoluments["item_no"].astype(str).isin(["902", "903", "912", "929"]),
            ["key", "value_rs"],
        ]
        .groupby("key", as_index=False)["value_rs"]
        .sum()
        .rename(columns={"value_rs": "emoluments_value_rs"})
    )

    frame = base.merge(reference, on="key", how="left", validate="one_to_one")
    for part in (gva, total_workers, hired_workers, emoluments):
        frame = frame.merge(part, on="key", how="left", validate="one_to_one")
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
    frame["annual_emoluments"] = frame["emoluments_value_rs"] * frame["annual_factor"]
    worker_columns = [
        "full_time_male", "full_time_female", "full_time_trans",
        "part_time_male", "part_time_female", "part_time_trans",
    ]
    frame[worker_columns] = frame[worker_columns].fillna(0)
    hired_columns = ["formal_hired_workers", "informal_hired_workers"]
    frame[hired_columns] = frame[hired_columns].fillna(0)
    frame["hired_workers"] = frame[hired_columns].sum(axis=1)
    frame["female_workers"] = frame["full_time_female"] + frame["part_time_female"]
    frame["all_gender_workers"] = (
        frame["full_time_male"] + frame["full_time_female"] + frame["full_time_trans"]
        + frame["part_time_male"] + frame["part_time_female"] + frame["part_time_trans"]
    )
    return frame


def ratio_rse(frame: pd.DataFrame, domain: pd.Series) -> tuple[float, float]:
    """MoSPI Appendix B SRSWR approximation for a combined ratio estimate.

    Unsampled domain units contribute zero within their sampled PSU. The FSU
    contribution is multiplied by the number of sampled FSUs in its
    stratum/sub-stratum, matching the notation in ASUSE Appendix B section 6.
    """
    work = frame.copy()
    market = work["non_profit"].ne(1) & work["major_nic_5dig"].ne(70_100)
    eligible = domain.reindex(work.index, fill_value=False) & market
    work["y"] = np.where(eligible, work["annual_gva"], 0.0)
    work["x"] = np.where(eligible, work["total_workers"], 0.0)
    y_hat = float((work["y"] * work["weight"]).sum())
    x_hat = float((work["x"] * work["weight"]).sum())
    ratio = y_hat / x_hat
    work["residual"] = work["weight"] * (work["y"] - ratio * work["x"])

    mse = 0.0
    strata = ["sector", "nss_region", "stratum", "sub_stratum"]
    for _, group in work.groupby(strata, dropna=False):
        psu = group.groupby("fsu_serial_no")["residual"].sum()
        n = len(psu)
        if n < 2:
            continue
        psu_contribution = n * psu
        stratum_residual = float(psu_contribution.sum() / n)
        mse += float(((psu_contribution - stratum_residual) ** 2).sum() / (n * (n - 1)))
    rse = 100.0 * math.sqrt(mse) / x_hat / abs(ratio)
    return ratio, rse


def summarize_asuse(frame: pd.DataFrame) -> tuple[list[dict], dict]:
    sectors: list[dict] = []
    for nic, group in frame.groupby("major_nic_2dig"):
        if len(group) < 30:
            continue
        establishments = group["weight"].sum()
        market_group = group.loc[group["annual_gva"].notna()]
        record = {
            "nic2": int(nic),
            "label": NIC2.get(int(nic), f"NIC {int(nic):02d}"),
            "sample_establishments": int(len(group)),
            "estimated_establishments": round(float(establishments)),
            "hwe_share": weighted_share(group, group["est_type"].eq(1)),
            "workers_per_establishment": weighted_ratio(group, "total_workers", "establishment_unit"),
            "gva_per_worker": weighted_ratio(market_group, "annual_gva", "total_workers"),
            "female_worker_share": weighted_ratio(group, "female_workers", "all_gender_workers"),
            "computer_use_share": weighted_share(group, group["used_computer"].eq(1)),
            "internet_use_share": weighted_share(group, group["used_internet"].eq(1)),
            "accounts_share": weighted_share(group, group["accounts_maintained"].eq(1)),
            "bank_account_share": weighted_share(group, group["bank_account"].isin([1, 2])),
        }
        sectors.append(record)

    frame = frame.copy()
    frame["establishment_unit"] = 1.0
    # Recompute because sector summaries above need this denominator in the source frame.
    for record in sectors:
        group = frame.loc[frame["major_nic_2dig"].eq(record["nic2"])]
        record["workers_per_establishment"] = weighted_ratio(group, "total_workers", "establishment_unit")

    tiers = {}
    for code, key, label in [(2, "oae", "Own-account enterprise"), (1, "hwe", "Hired-worker enterprise")]:
        group = frame.loc[frame["est_type"].eq(code)]
        market_group = group.loc[group["annual_gva"].notna()]
        tiers[key] = {
            "label": label,
            "sample_establishments": int(len(group)),
            "estimated_establishments": round(float(group["weight"].sum())),
            "estimated_workers": round(float((group["total_workers"] * group["weight"]).sum())),
            "workers_per_establishment": weighted_ratio(group, "total_workers", "establishment_unit"),
            "gva_per_worker": weighted_ratio(market_group, "annual_gva", "total_workers"),
            "female_worker_share": weighted_ratio(group, "female_workers", "all_gender_workers"),
        }
    return sectors, tiers


def plfs_frame() -> pd.DataFrame:
    daily_fields = [
        field
        for day in range(1, 8)
        for activity in plfs_daily_activity_fields(day)
        for field in activity
    ]

    columns = [
        "state_perv1", "b1q3_perv1", "nss_region_perv1", "b1q5_perv1",
        "b1q6_perv1", "b1q11_perv1", "b1q1_perv1", "b4q5_perv1",
        "b5pt1q3_perv1", "b5pt1q5_perv1", "b5pt1q10_perv1",
        "b5pt1q11_perv1", "b5pt1q12_perv1", "b5pt1q13_perv1",
        "b5pt2q3_perv1", "b5pt2q5_perv1", "b5pt2q9_perv1",
        "b5pt2q10_perv1", "b5pt2q11_perv1", "b5pt2q12_perv1",
        "b6q5_perv1", "b6q6_perv1", "b6q9_perv1", "b6q10_perv1",
        "mult_perv1", *daily_fields,
    ]
    with zipfile.ZipFile(PLFS_ZIP) as archive:
        member = next(name for name in archive.namelist() if name.endswith("/perv1.csv"))
        frame = pd.read_csv(archive.open(member), usecols=columns, low_memory=False)

    principal = frame["b5pt1q3_perv1"].isin(PLFS_EMPLOYED_STATUSES)
    subsidiary = frame["b5pt2q3_perv1"].isin(PLFS_EMPLOYED_STATUSES)
    frame["usual_employed"] = principal | subsidiary
    frame["status"] = np.where(principal, frame["b5pt1q3_perv1"], frame["b5pt2q3_perv1"])
    frame["nic"] = np.where(principal, frame["b5pt1q5_perv1"], frame["b5pt2q5_perv1"])
    frame["enterprise_size_code"] = np.where(
        principal, frame["b5pt1q10_perv1"], frame["b5pt2q9_perv1"]
    )
    frame["contract_code"] = np.where(
        principal, frame["b5pt1q11_perv1"], frame["b5pt2q10_perv1"]
    )
    frame["paid_leave_code"] = np.where(
        principal, frame["b5pt1q12_perv1"], frame["b5pt2q11_perv1"]
    )
    frame["social_security_code"] = np.where(
        principal, frame["b5pt1q13_perv1"], frame["b5pt2q12_perv1"]
    )
    frame["state"] = (
        pd.to_numeric(frame["state_perv1"], errors="coerce")
        .astype("Int64").astype("string").str.zfill(2)
    )
    frame["manufacturing"] = (
        frame["usual_employed"]
        & pd.to_numeric(frame["nic"], errors="coerce").between(10_000, 33_999)
    )
    frame["weight"] = pd.to_numeric(frame["mult_perv1"], errors="coerce").fillna(0.0)
    frame["sex_category"] = np.select(
        [frame["b4q5_perv1"].isin([1, 3]), frame["b4q5_perv1"].eq(2)],
        ["male", "female"], default=None,
    )
    frame["sector_category"] = np.select(
        [frame["b1q3_perv1"].eq(1), frame["b1q3_perv1"].eq(2)],
        ["rural", "urban"], default=None,
    )

    frame["_design_sector"] = pd.to_numeric(frame["b1q3_perv1"], errors="coerce").astype("Int64")
    frame["_design_region"] = pd.to_numeric(frame["nss_region_perv1"], errors="coerce").astype("Int64")
    frame["_design_stratum_code"] = pd.to_numeric(frame["b1q5_perv1"], errors="coerce").astype("Int64")
    rural_substratum = pd.to_numeric(frame["b1q6_perv1"], errors="coerce").astype("Int64").astype("string")
    frame["_design_rural_substratum"] = np.where(
        frame["_design_sector"].eq(1), rural_substratum, "urban"
    )
    frame["_subsample"] = pd.to_numeric(frame["b1q11_perv1"], errors="coerce").astype("Int64")
    frame["_fsu"] = pd.to_numeric(frame["b1q1_perv1"], errors="coerce").astype("Int64").astype("string")
    frame["_design_valid"] = (
        frame["state"].notna()
        & frame["_design_sector"].isin([1, 2])
        & frame["_design_region"].notna()
        & frame["_design_stratum_code"].notna()
        & pd.Series(frame["_design_rural_substratum"], index=frame.index).notna()
        & frame["_subsample"].isin([1, 2])
    )
    frame["_design_stratum"] = (
        frame["state"].astype("string") + "|"
        + frame["_design_sector"].astype("string") + "|"
        + frame["_design_region"].astype("string") + "|"
        + frame["_design_stratum_code"].astype("string") + "|"
        + pd.Series(frame["_design_rural_substratum"], index=frame.index, dtype="string")
    )
    frame["_fsu_key"] = frame["_design_stratum"] + "|" + frame["_fsu"]
    return frame


def plfs_summary(frame: pd.DataFrame) -> dict:
    frame = frame.loc[frame["state"].eq(TN) & frame["usual_employed"]].copy()

    def share(group: pd.DataFrame) -> float:
        return 100.0 * weighted_share(group, group["manufacturing"])

    manufacturing = frame.loc[frame["manufacturing"]].copy()
    status_shares = {
        "self_employed": weighted_share(manufacturing, manufacturing["status"].isin([11, 12, 21])),
        "regular_wage": weighted_share(manufacturing, manufacturing["status"].eq(31)),
        "casual_labour": weighted_share(manufacturing, manufacturing["status"].isin([41, 51])),
    }
    return {
        "sample_workers": int(len(frame)),
        "sample_manufacturing_workers": int(len(manufacturing)),
        "manufacturing_share": share(frame),
        "male_manufacturing_share": share(frame.loc[frame["b4q5_perv1"].isin([1, 3])]),
        "female_manufacturing_share": share(frame.loc[frame["b4q5_perv1"].eq(2)]),
        "rural_manufacturing_share": share(frame.loc[frame["b1q3_perv1"].eq(1)]),
        "urban_manufacturing_share": share(frame.loc[frame["b1q3_perv1"].eq(2)]),
        "manufacturing_status_shares": status_shares,
    }


def plfs_design_scaffold(frame: pd.DataFrame) -> tuple[pd.MultiIndex, bool]:
    valid = frame.loc[frame["_design_valid"], ["_design_stratum", "_subsample"]].drop_duplicates()
    strata = valid["_design_stratum"].drop_duplicates().sort_values()
    scaffold = pd.MultiIndex.from_product(
        [strata, [1, 2]], names=["_design_stratum", "_subsample"]
    )
    observed = pd.MultiIndex.from_frame(valid)
    return scaffold, bool(len(scaffold) and scaffold.isin(observed).all())


def plfs_estimate_cell(
    observations: pd.DataFrame,
    scaffold: pd.MultiIndex,
    scaffold_complete: bool,
    *,
    binary: bool,
    positive_mean: bool = False,
) -> dict:
    observations = observations.loc[
        observations["weight"].gt(0) & np.isfinite(observations["_value"])
    ].copy()
    sample_count = int(len(observations))
    weights = observations["weight"].clip(lower=0.0)
    values = observations["_value"]
    denominator = float(weights.sum())
    weighted_values = weights * values
    estimate = float(weighted_values.sum() / denominator) if denominator > 0 else math.nan
    kish_effective_n = (
        float(denominator ** 2 / weights.pow(2).sum())
        if denominator > 0 and weights.pow(2).sum() > 0 else 0.0
    )
    maximum_weight_share = float(weights.max() / denominator) if denominator > 0 else 0.0
    active_fsu_count = int(observations.loc[observations["_fsu"].notna(), "_fsu_key"].nunique())

    variance_computable = (
        scaffold_complete
        and denominator > 0
        and not observations.empty
        and observations["_design_valid"].all()
        and math.isfinite(estimate)
    )
    standard_error = math.nan
    rse = math.nan
    if variance_computable:
        totals = (
            observations.assign(_weighted_y=weighted_values, _weighted_x=weights)
            .groupby(["_design_stratum", "_subsample"])[["_weighted_y", "_weighted_x"]]
            .sum()
            .reindex(scaffold, fill_value=0.0)
        )
        y1 = totals.xs(1, level="_subsample")["_weighted_y"]
        y2 = totals.xs(2, level="_subsample")["_weighted_y"]
        x1 = totals.xs(1, level="_subsample")["_weighted_x"]
        x2 = totals.xs(2, level="_subsample")["_weighted_x"]
        variance = float((((y1 - y2) - estimate * (x1 - x2)) ** 2).sum() / denominator ** 2)
        variance_computable = math.isfinite(variance) and variance >= 0
        if variance_computable:
            standard_error = math.sqrt(variance)
            rse = standard_error / abs(estimate) if estimate != 0 else math.inf

    reasons = []
    if sample_count < PLFS_MIN_SAMPLE:
        reasons.append(f"sample count below {PLFS_MIN_SAMPLE}")
    if active_fsu_count < PLFS_MIN_ACTIVE_FSUS:
        reasons.append(f"active FSU count below {PLFS_MIN_ACTIVE_FSUS}")
    if kish_effective_n < PLFS_MIN_EFFECTIVE_N:
        reasons.append(f"Kish effective sample size below {PLFS_MIN_EFFECTIVE_N}")
    if maximum_weight_share > PLFS_MAX_WEIGHT_SHARE:
        reasons.append(f"largest denominator-weight share exceeds {PLFS_MAX_WEIGHT_SHARE:.0%}")
    if not variance_computable:
        reasons.append("official paired-subsample variance cannot be computed")
    elif rse > PLFS_MAX_RSE:
        reasons.append(f"design-based RSE exceeds {PLFS_MAX_RSE:.0%}")

    quality = {
        "sample_count": sample_count,
        "active_fsu_count": active_fsu_count,
        "kish_effective_n": kish_effective_n,
        "maximum_weight_share": maximum_weight_share,
    }
    if binary:
        yes_count = int(values.eq(1).sum())
        no_count = int(values.eq(0).sum())
        quality.update(unweighted_yes_count=yes_count, unweighted_no_count=no_count)
        if yes_count < PLFS_MIN_BINARY_OUTCOMES:
            reasons.append(f"sampled outcomes below {PLFS_MIN_BINARY_OUTCOMES}")
        if no_count < PLFS_MIN_BINARY_OUTCOMES:
            reasons.append(f"sampled non-outcomes below {PLFS_MIN_BINARY_OUTCOMES}")
    else:
        absolute_total = float(weighted_values.abs().sum())
        outcome_share = (
            float(weighted_values.abs().max() / absolute_total) if absolute_total > 0 else 0.0
        )
        quality["maximum_weighted_outcome_share"] = outcome_share
        if outcome_share > PLFS_MAX_OUTCOME_SHARE:
            reasons.append(
                f"largest absolute weighted-earnings contribution exceeds {PLFS_MAX_OUTCOME_SHARE:.0%}"
            )

    stability = (
        "suppressed" if reasons else
        "stable" if rse <= PLFS_STABLE_RSE else
        "low_precision"
    )
    ci_lower = estimate - 1.96 * standard_error if stability != "suppressed" else math.nan
    ci_upper = estimate + 1.96 * standard_error if stability != "suppressed" else math.nan
    if stability != "suppressed" and binary:
        ci_lower, ci_upper = max(0.0, ci_lower), min(1.0, ci_upper)
    elif stability != "suppressed" and positive_mean:
        ci_lower = max(0.0, ci_lower)

    return {
        **quality,
        "estimate": estimate if stability != "suppressed" else None,
        "standard_error": standard_error if stability != "suppressed" else None,
        "rse": rse if stability != "suppressed" else None,
        "ci95_lower": ci_lower if stability != "suppressed" else None,
        "ci95_upper": ci_upper if stability != "suppressed" else None,
        "stability": stability,
        "suppression_reason": "; ".join(reasons) if reasons else None,
    }


def plfs_output_rows(
    full_frame: pd.DataFrame,
    observations: pd.DataFrame,
    scaffold: pd.MultiIndex,
    scaffold_complete: bool,
    *,
    concept: str,
    concept_label: str,
    unit: str,
    recall_period: str,
    sample_unit: str,
    binary: bool,
    positive_mean: bool = False,
    include_enterprise_size: bool = False,
) -> list[dict]:
    rows = []
    subgroup_geographies = ["IN", TN, *PEER_CODES, *SENSITIVITY_CODES]
    all_states = sorted(full_frame["state"].dropna().unique())

    def append_row(
        geography_id: str,
        geography_label: str,
        geography_type: str,
        dimension: str,
        category_id: str,
        category_label: str,
        group: pd.DataFrame,
    ) -> None:
        rows.append({
            "survey": "plfs", "year": "2023-24", "concept": concept,
            "concept_label": concept_label, "dimension": dimension,
            "geography_id": geography_id, "geography_label": geography_label,
            "geography_type": geography_type, "category_id": category_id,
            "category_label": category_label, "unit": unit,
            "recall_period": recall_period, "sample_unit": sample_unit,
            **plfs_estimate_cell(
                group, scaffold, scaffold_complete, binary=binary,
                positive_mean=positive_mean,
            ),
        })

    for geography_id in ["IN", *all_states]:
        geography_label = "India" if geography_id == "IN" else STATE_LABELS.get(
            geography_id, f"State/UT {geography_id}"
        )
        geography_type = "country" if geography_id == "IN" else "state"
        group = observations if geography_id == "IN" else observations.loc[
            observations["state"].eq(geography_id)
        ]
        append_row(
            geography_id, geography_label, geography_type,
            "overall", "all", "All", group,
        )

    sex_labels = {
        "male": "Male (official convention; includes sex code 3)",
        "female": "Female",
    }
    sector_labels = {"rural": "Rural", "urban": "Urban"}
    size_labels = {"1": "Fewer than 6", "2": "6-9", "3": "10-19", "4": "20+", "9": "Unknown"}
    for geography_id in subgroup_geographies:
        geography_label = "India" if geography_id == "IN" else STATE_LABELS[geography_id]
        geography_type = "country" if geography_id == "IN" else "state"
        geography = observations if geography_id == "IN" else observations.loc[
            observations["state"].eq(geography_id)
        ]
        for category_id, category_label in sex_labels.items():
            append_row(
                geography_id, geography_label, geography_type,
                "sex", category_id, category_label,
                geography.loc[geography["sex_category"].eq(category_id)],
            )
        for category_id, category_label in sector_labels.items():
            append_row(
                geography_id, geography_label, geography_type,
                "sector", category_id, category_label,
                geography.loc[geography["sector_category"].eq(category_id)],
            )
        if include_enterprise_size:
            size_codes = pd.to_numeric(geography["enterprise_size_code"], errors="coerce").astype("Int64")
            for category_id, category_label in size_labels.items():
                append_row(
                    geography_id, geography_label, geography_type,
                    "enterprise_size", category_id, category_label,
                    geography.loc[size_codes.eq(int(category_id))],
                )
    return rows


def plfs_worker_earnings(
    frame: pd.DataFrame, scaffold: pd.MultiIndex, scaffold_complete: bool
) -> list[dict]:
    cws_status = pd.to_numeric(frame["b6q5_perv1"], errors="coerce")
    cws_industry = pd.to_numeric(frame["b6q6_perv1"], errors="coerce")
    regular_value = pd.to_numeric(frame["b6q9_perv1"], errors="coerce")
    self_employed_value = pd.to_numeric(frame["b6q10_perv1"], errors="coerce")

    regular = frame.loc[
        cws_status.isin(PLFS_REGULAR_STATUSES)
        & cws_industry.between(10, 33)
        & regular_value.gt(0)
    ].copy()
    regular["_value"] = regular_value.loc[regular.index]

    self_employed = frame.loc[
        cws_status.isin(PLFS_SELF_EMPLOYED_STATUSES)
        & cws_industry.between(10, 33)
        & self_employed_value.ne(0)
        & self_employed_value.notna()
    ].copy()
    self_employed["_value"] = self_employed_value.loc[self_employed.index]

    casual_days = []
    carry = [
        "state", "weight", "sex_category", "sector_category", "_design_valid",
        "_design_stratum", "_subsample", "_fsu", "_fsu_key",
    ]
    for day in range(1, 8):
        total = pd.Series(0.0, index=frame.index)
        for status_field, industry_field, earnings_field in plfs_daily_activity_fields(day):
            status = pd.to_numeric(frame[status_field], errors="coerce")
            industry = pd.to_numeric(frame[industry_field], errors="coerce")
            earnings = pd.to_numeric(frame[earnings_field], errors="coerce")
            qualifies = (
                status.isin(PLFS_CASUAL_STATUSES)
                & industry.between(10, 33)
                & earnings.gt(0)
            )
            total = total.add(earnings.where(qualifies, 0.0), fill_value=0.0)
        day_frame = frame.loc[total.gt(0), carry].copy()
        day_frame["_value"] = total.loc[day_frame.index]
        casual_days.append(day_frame)
    casual = pd.concat(casual_days, ignore_index=True)

    return [
        *plfs_output_rows(
            frame, regular, scaffold, scaffold_complete,
            concept="regular_monthly_earnings",
            concept_label="Monthly regular wage/salaried earnings",
            unit="rupees per month", recall_period="preceding calendar month",
            sample_unit="persons", binary=False, positive_mean=True,
        ),
        *plfs_output_rows(
            frame, self_employed, scaffold, scaffold_complete,
            concept="self_employment_30_day_gross_earnings",
            concept_label="Gross self-employment earnings in the last 30 days",
            unit="rupees per 30 days (gross)", recall_period="last 30 days",
            sample_unit="persons", binary=False,
        ),
        *plfs_output_rows(
            frame, casual, scaffold, scaffold_complete,
            concept="casual_person_day_earnings",
            concept_label="Casual earnings per person-day",
            unit="rupees per person-day", recall_period="previous 7 days",
            sample_unit="person-days", binary=False, positive_mean=True,
        ),
    ]


def plfs_worker_job_quality(
    frame: pd.DataFrame, scaffold: pd.MultiIndex, scaffold_complete: bool
) -> list[dict]:
    regular_manufacturing = frame.loc[
        frame["usual_employed"] & frame["status"].eq(31) & frame["manufacturing"]
    ].copy()
    specifications = [
        ("written_contract", "Has a written job contract", "contract_code", {1, 2, 3, 4}, {2, 3, 4}),
        ("paid_leave", "Eligible for paid leave", "paid_leave_code", {1, 2}, {1}),
        ("specified_social_security", "Eligible for a specified social-security benefit", "social_security_code", set(range(1, 10)), set(range(1, 8))),
        ("no_social_security", "Not eligible for a specified social-security benefit", "social_security_code", set(range(1, 10)), {8}),
        ("unknown_social_security", "Social-security eligibility not known", "social_security_code", set(range(1, 10)), {9}),
    ]
    rows = []
    for concept, label, field, denominator_codes, numerator_codes in specifications:
        codes = pd.to_numeric(regular_manufacturing[field], errors="coerce")
        observations = regular_manufacturing.loc[codes.isin(denominator_codes)].copy()
        observations["_value"] = codes.loc[observations.index].isin(numerator_codes).astype(float)
        rows.extend(plfs_output_rows(
            frame, observations, scaffold, scaffold_complete,
            concept=concept, concept_label=label, unit="proportion",
            recall_period="usual status (principal activity preferred; subsidiary otherwise)",
            sample_unit="persons", binary=True, include_enterprise_size=True,
        ))

    return rows


def asi_summary() -> tuple[dict, list[dict]]:
    frame = pd.read_csv(ASI_PANEL, dtype={"state": "string"})
    tn = frame.loc[(frame["year"].eq(2023)) & frame["state"].str.zfill(2).eq(TN)].copy()
    overall = tn.loc[tn["sector_id"].eq("all-manufacturing")].iloc[0]
    tier = {
        "label": "Registered factory",
        "sample_factories": int(overall["sample_factories"]),
        "estimated_factories": round(float(overall["estimated_factories"])),
        "persons_engaged": round(float(overall["employees"])),
        "persons_per_factory": float(overall["employees"] / overall["estimated_factories"]),
        "gva_per_person_engaged": float(overall["gva_per_worker"]),
        "female_direct_worker_share": float(overall["female_direct_worker_share"]),
        "contract_worker_share": float(overall["contract_worker_share"]),
        "rd_factory_share": float(overall["rd_unit_share"]),
        "training_factory_share": float(overall["training_factory_share"]),
    }
    labels = {
        "automobile-core": "Motor vehicles",
        "electronics-core": "Electronics",
        "food-processing": "Food processing",
        "leather-footwear": "Leather & footwear",
        "life-sciences": "Life sciences",
        "textiles-apparel": "Textiles & apparel",
    }
    sectors = []
    for sector_id, label in labels.items():
        row = tn.loc[tn["sector_id"].eq(sector_id)].iloc[0]
        sectors.append({
            "id": sector_id,
            "label": label,
            "estimated_factories": round(float(row["estimated_factories"])),
            "persons_engaged": round(float(row["employees"])),
            "gva_per_person_engaged": float(row["gva_per_worker"]),
            "female_direct_worker_share": float(row["female_direct_worker_share"]),
            "contract_worker_share": float(row["contract_worker_share"]),
            "rd_factory_share": float(row["rd_unit_share"]),
            "training_factory_share": float(row["training_factory_share"]),
            "sample_factories": int(row["sample_factories"]),
            "stability": row["stability"],
        })
    return tier, sectors


def size_band(values: pd.Series, include_zero: bool = False) -> pd.Series:
    numeric_values = pd.to_numeric(values, errors="coerce")
    choices = [band["id"] for band in SIZE_BANDS]
    conditions = [
        numeric_values.eq(1), numeric_values.between(2, 4), numeric_values.between(5, 9),
        numeric_values.between(10, 19), numeric_values.between(20, 49),
        numeric_values.between(50, 99), numeric_values.between(100, 249),
        numeric_values.ge(250),
    ]
    default = "zero-unclassified" if include_zero else None
    return pd.Series(np.select(conditions, choices, default=default), index=values.index, dtype="string")


def geography_groups(frame: pd.DataFrame, states: list[str] | None = None):
    yield "IN", "India", "country", frame
    codes = states if states is not None else sorted(frame["state"].dropna().unique())
    for code in codes:
        yield code, STATE_LABELS.get(code, f"State/UT {code}"), "state", frame.loc[frame["state"].eq(code)]


def cell_quality(group: pd.DataFrame) -> dict:
    sample_count = int(len(group))
    employment = group["employment_contribution"].clip(lower=0)
    total = float(employment.sum())
    concentration = float(employment.max() / total) if total else 0.0
    reasons = []
    if sample_count < MIN_SAMPLE:
        reasons.append(f"sample count below {MIN_SAMPLE}")
    if concentration > MAX_EMPLOYMENT_CONCENTRATION:
        reasons.append(f"largest weighted-employment contribution exceeds {MAX_EMPLOYMENT_CONCENTRATION:.0%}")
    return {
        "sample_count": sample_count,
        "weighted_employment_concentration": concentration,
        "stability": "suppressed" if reasons else "stable",
        "suppression_reason": "; ".join(reasons) if reasons else None,
    }


def suppress_unstable(row: dict, estimate_fields: tuple[str, ...]) -> dict:
    if row["stability"] == "suppressed":
        for field in estimate_fields:
            row[field] = None
    return row


def outcome_cell(group: pd.DataFrame, numerator: str, denominator: str) -> dict:
    weighted_numerator = group[numerator].fillna(0.0) * group["weight"]
    weighted_denominator = group[denominator].fillna(0.0).clip(lower=0.0) * group["weight"]
    absolute_numerator = weighted_numerator.abs()
    denominator_total = float(weighted_denominator.sum())
    numerator_total = float(weighted_numerator.sum())
    denominator_concentration = (
        float(weighted_denominator.max() / denominator_total) if denominator_total > 0 else 0.0
    )
    absolute_numerator_total = float(absolute_numerator.sum())
    numerator_concentration = (
        float(absolute_numerator.max() / absolute_numerator_total)
        if absolute_numerator_total > 0 else 0.0
    )
    reasons = []
    if len(group) < MIN_SAMPLE:
        reasons.append(f"sample count below {MIN_SAMPLE}")
    if denominator_concentration > MAX_EMPLOYMENT_CONCENTRATION:
        reasons.append(
            f"largest weighted-denominator contribution exceeds {MAX_EMPLOYMENT_CONCENTRATION:.0%}"
        )
    if numerator_concentration > MAX_EMPLOYMENT_CONCENTRATION:
        reasons.append(
            f"largest absolute weighted-numerator contribution exceeds {MAX_EMPLOYMENT_CONCENTRATION:.0%}"
        )
    stable = not reasons
    return {
        "sample_count": int(len(group)),
        "weighted_denominator_concentration": denominator_concentration,
        "absolute_weighted_numerator_concentration": numerator_concentration,
        "stability": "stable" if stable else "suppressed",
        "suppression_reason": None if stable else "; ".join(reasons),
        "_numerator_total": numerator_total,
        "_denominator_total": denominator_total,
    }


def layer5_source_row(rows: list[dict], specification: dict, geography_id: str) -> dict:
    matches = [
        row for row in rows
        if row["survey"] == specification["survey"]
        and row["dimension"] == "overall"
        and row["geography_id"] == geography_id
        and row.get("concept") == specification.get("concept")
    ]
    if len(matches) != 1:
        raise AssertionError(
            f"Expected one Layer 5 source row for {specification['outcome']} / {geography_id}; "
            f"found {len(matches)}"
        )
    return matches[0]


def peer_comparisons_raw(source_arrays: dict[str, list[dict]]) -> list[dict]:
    rows = []
    uncertainty_fields = ["standard_error", "rse", "ci95_lower", "ci95_upper"]
    for specification in LAYER5_RAW_OUTCOMES:
        sources = source_arrays[specification["source"]]
        tn_source = layer5_source_row(sources, specification, TN)
        for comparator in LAYER5_COMPARATORS:
            comparator_source = layer5_source_row(sources, specification, comparator["id"])
            tn_estimate = tn_source.get(specification["value_field"])
            comparator_estimate = comparator_source.get(specification["value_field"])
            suppressed_sides = []
            for side, source, estimate in [
                ("Tamil Nadu", tn_source, tn_estimate),
                (comparator["label"], comparator_source, comparator_estimate),
            ]:
                if source["stability"] == "suppressed" or estimate is None:
                    reason = source.get("suppression_reason") or "source estimate unavailable or required denominator non-positive"
                    suppressed_sides.append(f"{side}: {reason}")
            is_proportion = specification.get("is_proportion", False)
            stability = (
                "suppressed" if suppressed_sides
                else "low_precision"
                if specification["survey"] == "plfs"
                and "low_precision" in {tn_source["stability"], comparator_source["stability"]}
                else "stable"
            )
            absolute_gap = (
                tn_estimate - comparator_estimate
                if stability != "suppressed" else None
            )
            ratio = (
                tn_estimate / comparator_estimate
                if stability != "suppressed" and not is_proportion and comparator_estimate > 0
                else None
            )
            row = {
                "survey": specification["survey"],
                "year": "2023-24",
                "outcome": specification["outcome"],
                "outcome_label": specification["label"],
                "outcome_family": specification["family"],
                "unit": specification["unit"],
                "is_proportion": is_proportion,
                "comparator_id": comparator["id"],
                "comparator_label": comparator["label"],
                "comparator_type": comparator["type"],
                "tn_estimate": tn_estimate,
                "comparator_estimate": comparator_estimate,
                "absolute_gap": absolute_gap,
                "gap_display_unit": "percentage_points" if is_proportion else specification["unit"],
                "relative_ratio": ratio,
                "relative_gap_percent": 100.0 * (ratio - 1.0) if ratio is not None else None,
                "stability": stability,
                "suppression_reason": "; ".join(suppressed_sides) if suppressed_sides else None,
            }
            for field in uncertainty_fields:
                row[f"tn_{field}"] = tn_source.get(field) if specification["survey"] == "plfs" else None
                row[f"comparator_{field}"] = comparator_source.get(field) if specification["survey"] == "plfs" else None
            rows.append(row)
    return rows


def layer5_cell_definitions(frame: pd.DataFrame, dimension: str) -> list[tuple[str, str, pd.Series]]:
    industries = [
        (group["id"], group["label"], frame["nic2"].isin(group["nic2"]))
        for group in LAYER5_INDUSTRY_GROUPS
    ]
    sizes = [
        (group["id"], group["label"], frame["size_band"].isin(group["size_bands"]))
        for group in LAYER5_SIZE_GROUPS
    ]
    if dimension == "industry":
        return industries
    if dimension == "size":
        return sizes
    if dimension == "industry_size":
        return [
            (
                f"{industry_id}__{size_id}",
                f"{industry_label} / {size_label}",
                industry_mask & size_mask,
            )
            for industry_id, industry_label, industry_mask in industries
            for size_id, size_label, size_mask in sizes
        ]
    raise ValueError(f"Unsupported Layer 5 adjustment dimension: {dimension}")


def layer5_support_cells(
    frame: pd.DataFrame, numerator: str, denominator: str, dimension: str
) -> list[dict]:
    cells = []
    for cell_id, cell_label, mask in layer5_cell_definitions(frame, dimension):
        quality = outcome_cell(frame.loc[mask], numerator, denominator)
        cells.append({"cell_id": cell_id, "cell_label": cell_label, **quality})
    return cells


def pairwise_standardization(tn_cells: list[dict], comparator_cells: list[dict]) -> dict:
    comparator_by_id = {cell["cell_id"]: cell for cell in comparator_cells}
    retained = []
    for tn_cell in tn_cells:
        comparator_cell = comparator_by_id[tn_cell["cell_id"]]
        if (
            tn_cell["stability"] == "stable"
            and comparator_cell["stability"] == "stable"
            and tn_cell["_denominator_total"] > 0
            and comparator_cell["_denominator_total"] > 0
        ):
            retained.append((tn_cell, comparator_cell))

    tn_denominator = math.fsum(cell[0]["_denominator_total"] for cell in retained)
    comparator_denominator = math.fsum(cell[1]["_denominator_total"] for cell in retained)
    if len(retained) < 2 or tn_denominator <= 0 or comparator_denominator <= 0:
        return {"retained": retained, "components": []}

    components = []
    for tn_cell, comparator_cell in retained:
        tn_rate = tn_cell["_numerator_total"] / tn_cell["_denominator_total"]
        comparator_rate = comparator_cell["_numerator_total"] / comparator_cell["_denominator_total"]
        tn_weight = tn_cell["_denominator_total"] / tn_denominator
        comparator_weight = comparator_cell["_denominator_total"] / comparator_denominator
        common_weight = 0.5 * (tn_weight + comparator_weight)
        components.append({
            "cell_id": tn_cell["cell_id"],
            "cell_label": tn_cell["cell_label"],
            "tn_cell_rate": tn_rate,
            "comparator_cell_rate": comparator_rate,
            "tn_weight": tn_weight,
            "comparator_weight": comparator_weight,
            "common_weight": common_weight,
            "cell_composition_component": 0.5 * (tn_weight - comparator_weight) * (tn_rate + comparator_rate),
            "cell_within_component": 0.5 * (tn_rate - comparator_rate) * (tn_weight + comparator_weight),
        })

    common_support_tn = math.fsum(component["tn_weight"] * component["tn_cell_rate"] for component in components)
    common_support_comparator = math.fsum(component["comparator_weight"] * component["comparator_cell_rate"] for component in components)
    standardized_tn = math.fsum(component["common_weight"] * component["tn_cell_rate"] for component in components)
    standardized_comparator = math.fsum(component["common_weight"] * component["comparator_cell_rate"] for component in components)
    composition_component = math.fsum(component["cell_composition_component"] for component in components)
    within_component = math.fsum(component["cell_within_component"] for component in components)
    common_support_raw_gap = common_support_tn - common_support_comparator
    adjusted_gap = standardized_tn - standardized_comparator
    return {
        "retained": retained,
        "components": components,
        "common_support_tn": common_support_tn,
        "common_support_comparator": common_support_comparator,
        "common_support_raw_gap": common_support_raw_gap,
        "standardized_tn": standardized_tn,
        "standardized_comparator": standardized_comparator,
        "adjusted_gap": adjusted_gap,
        "composition_component": composition_component,
        "within_component": within_component,
        "decomposition_residual": common_support_raw_gap - composition_component - within_component,
    }


def peer_comparisons_adjusted(
    outcome_frames: dict[str, pd.DataFrame], raw_rows: list[dict]
) -> list[dict]:
    raw_by_key = {(row["outcome"], row["comparator_id"]): row for row in raw_rows}
    classifications = {
        "industry": "project_broad_industry_7",
        "size": "common_size_4",
        "industry_size": "broad_industry_7_x_common_size_4",
    }
    rows = []
    for specification in LAYER5_ADJUSTMENT_OUTCOMES:
        frame = outcome_frames[specification["outcome"]]
        tn_frame = frame.loc[frame["state"].eq(TN)]
        for dimension in specification["dimensions"]:
            total_cell_count = len(layer5_cell_definitions(frame, dimension))
            tn_cells = layer5_support_cells(
                tn_frame, specification["numerator"], specification["denominator"], dimension
            )
            tn_full_denominator = outcome_cell(
                tn_frame, specification["numerator"], specification["denominator"]
            )["_denominator_total"]
            for comparator in LAYER5_COMPARATORS:
                comparator_frame = frame if comparator["id"] == "IN" else frame.loc[
                    frame["state"].eq(comparator["id"])
                ]
                comparator_cells = layer5_support_cells(
                    comparator_frame, specification["numerator"], specification["denominator"], dimension
                )
                comparator_full_denominator = outcome_cell(
                    comparator_frame, specification["numerator"], specification["denominator"]
                )["_denominator_total"]
                decomposition = pairwise_standardization(tn_cells, comparator_cells)
                retained = decomposition["retained"]
                retained_tn_denominator = math.fsum(cell[0]["_denominator_total"] for cell in retained)
                retained_comparator_denominator = math.fsum(cell[1]["_denominator_total"] for cell in retained)
                tn_coverage = (
                    min(1.0, max(0.0, retained_tn_denominator / tn_full_denominator))
                    if tn_full_denominator > 0 else 0.0
                )
                comparator_coverage = (
                    min(1.0, max(0.0, retained_comparator_denominator / comparator_full_denominator))
                    if comparator_full_denominator > 0 else 0.0
                )
                raw = raw_by_key[(specification["outcome"], comparator["id"])]
                reasons = []
                if raw["stability"] == "suppressed":
                    reasons.append("full-universe raw comparison is suppressed")
                if len(retained) < 2:
                    reasons.append("fewer than two jointly stable positive-denominator cells remain")
                if tn_full_denominator <= 0 or retained_tn_denominator <= 0:
                    reasons.append("Tamil Nadu retained denominator is non-positive")
                if comparator_full_denominator <= 0 or retained_comparator_denominator <= 0:
                    reasons.append(f"{comparator['label']} retained denominator is non-positive")
                if tn_coverage < LAYER5_MIN_COVERAGE:
                    reasons.append(f"Tamil Nadu denominator coverage is below {LAYER5_MIN_COVERAGE:.0%}")
                if comparator_coverage < LAYER5_MIN_COVERAGE:
                    reasons.append(f"{comparator['label']} denominator coverage is below {LAYER5_MIN_COVERAGE:.0%}")
                if decomposition.get("components"):
                    finite_fields = [
                        "common_support_tn", "common_support_comparator", "common_support_raw_gap",
                        "standardized_tn", "standardized_comparator", "adjusted_gap",
                        "composition_component", "within_component", "decomposition_residual",
                    ]
                    if not all(math.isfinite(decomposition[field]) for field in finite_fields):
                        reasons.append("decomposition contains a non-finite value")
                    else:
                        tolerance = 1e-8 * max(1.0, abs(decomposition["common_support_raw_gap"]))
                        if abs(decomposition["adjusted_gap"] - decomposition["within_component"]) > tolerance:
                            reasons.append("adjusted-gap identity failed tolerance")
                        if abs(decomposition["decomposition_residual"]) > tolerance:
                            reasons.append("common-support decomposition identity failed tolerance")

                stable = not reasons
                row = {
                    "survey": specification["survey"],
                    "year": "2023-24",
                    "outcome": specification["outcome"],
                    "outcome_label": specification["label"],
                    "unit": specification["unit"],
                    "adjustment_dimension": dimension,
                    "classification": classifications[dimension],
                    "comparator_id": comparator["id"],
                    "comparator_label": comparator["label"],
                    "comparator_type": comparator["type"],
                    "full_raw_tn": raw["tn_estimate"] if stable else None,
                    "full_raw_comparator": raw["comparator_estimate"] if stable else None,
                    "full_raw_gap": raw["absolute_gap"] if stable else None,
                    "common_support_tn": decomposition.get("common_support_tn") if stable else None,
                    "common_support_comparator": decomposition.get("common_support_comparator") if stable else None,
                    "common_support_raw_gap": decomposition.get("common_support_raw_gap") if stable else None,
                    "tn_denominator_coverage": tn_coverage,
                    "comparator_denominator_coverage": comparator_coverage,
                    "retained_cell_count": len(retained),
                    "total_cell_count": total_cell_count,
                    "standardized_tn": decomposition.get("standardized_tn") if stable else None,
                    "standardized_comparator": decomposition.get("standardized_comparator") if stable else None,
                    "adjusted_gap": decomposition.get("adjusted_gap") if stable else None,
                    "composition_component": decomposition.get("composition_component") if stable else None,
                    "within_component": decomposition.get("within_component") if stable else None,
                    "decomposition_residual": decomposition.get("decomposition_residual") if stable else None,
                    "uncertainty_available": False,
                    "stability": "stable" if stable else "suppressed",
                    "suppression_reason": None if stable else "; ".join(reasons),
                    "components": decomposition.get("components", []) if stable else [],
                }
                rows.append(row)
    return rows


def validate_layer5_contract(structure_v1: dict, checks: list[dict]) -> None:
    """Fail before publication if the locked Layer 5 contract drifts."""
    raw_rows = structure_v1.get("peer_comparisons_raw")
    adjusted_rows = structure_v1.get("peer_comparisons_adjusted")
    if not isinstance(raw_rows, list) or len(raw_rows) != 78:
        raise AssertionError("Layer 5 requires exactly 78 raw comparison rows")
    if not isinstance(adjusted_rows, list) or len(adjusted_rows) != 78:
        raise AssertionError("Layer 5 requires exactly 78 adjusted comparison rows")

    comparators = {row["id"]: row for row in LAYER5_COMPARATORS}
    comparator_ids = set(comparators)
    raw_specs = {row["outcome"]: row for row in LAYER5_RAW_OUTCOMES}
    raw_keys = {(row.get("outcome"), row.get("comparator_id")) for row in raw_rows}
    expected_raw_keys = {
        (outcome, comparator_id)
        for outcome in raw_specs
        for comparator_id in comparator_ids
    }
    if len(raw_keys) != len(raw_rows) or raw_keys != expected_raw_keys:
        raise AssertionError("Layer 5 raw outcome/comparator coverage is incomplete or duplicated")

    source_arrays = {
        "value_addition": structure_v1["value_addition"],
        "establishment_compensation": structure_v1["establishment_compensation"],
        "worker_earnings": structure_v1["worker_earnings"],
        "worker_job_quality": structure_v1["worker_job_quality"],
    }
    uncertainty_fields = ["standard_error", "rse", "ci95_lower", "ci95_upper"]
    proportion_outcomes = {
        specification["outcome"]
        for specification in LAYER5_RAW_OUTCOMES
        if specification.get("is_proportion", False)
    }

    def require_finite(value, label: str) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            raise AssertionError(f"{label} must be finite")

    def require_close(actual: float, expected: float, label: str) -> None:
        if abs(actual - expected) > 1e-8 * max(1.0, abs(expected)):
            raise AssertionError(f"Layer 5 {label} drift")

    for row in raw_rows:
        specification = raw_specs[row["outcome"]]
        comparator = comparators[row["comparator_id"]]
        expected_metadata = {
            "survey": specification["survey"],
            "year": "2023-24",
            "outcome_label": specification["label"],
            "outcome_family": specification["family"],
            "unit": specification["unit"],
            "comparator_label": comparator["label"],
            "comparator_type": comparator["type"],
        }
        if any(row.get(field) != expected for field, expected in expected_metadata.items()):
            raise AssertionError(
                f"Layer 5 raw metadata drift for {row['outcome']} / {row['comparator_id']}"
            )
        tn_source = layer5_source_row(
            source_arrays[specification["source"]], specification, TN
        )
        comparator_source = layer5_source_row(
            source_arrays[specification["source"]], specification, row["comparator_id"]
        )
        value_field = specification["value_field"]
        tn_estimate = tn_source.get(value_field)
        comparator_estimate = comparator_source.get(value_field)
        if row.get("tn_estimate") != tn_estimate:
            raise AssertionError(f"Layer 5 Tamil Nadu source drift for {row['outcome']}")
        if row.get("comparator_estimate") != comparator_estimate:
            raise AssertionError(
                f"Layer 5 comparator source drift for {row['outcome']} / {row['comparator_id']}"
            )
        expected_stability = (
            "suppressed"
            if tn_source["stability"] == "suppressed"
            or comparator_source["stability"] == "suppressed"
            or tn_estimate is None
            or comparator_estimate is None
            else "low_precision"
            if specification["survey"] == "plfs"
            and "low_precision" in {tn_source["stability"], comparator_source["stability"]}
            else "stable"
        )
        if row.get("stability") != expected_stability:
            raise AssertionError(
                f"Layer 5 raw stability drift for {row['outcome']} / {row['comparator_id']}"
            )
        if expected_stability != "suppressed" and row.get("suppression_reason") is not None:
            raise AssertionError("Unsuppressed Layer 5 raw rows must not have a suppression reason")
        if row.get("is_proportion") != (row["outcome"] in proportion_outcomes):
            raise AssertionError(f"Layer 5 proportion flag drift for {row['outcome']}")
        for field in uncertainty_fields:
            expected_tn = tn_source.get(field) if row["survey"] == "plfs" else None
            expected_comparator = comparator_source.get(field) if row["survey"] == "plfs" else None
            if row.get(f"tn_{field}") != expected_tn or row.get(f"comparator_{field}") != expected_comparator:
                raise AssertionError(
                    f"Layer 5 uncertainty drift for {row['outcome']} / {row['comparator_id']}"
                )
        if any(re.search(r"gap.*(standard_error|rse|ci|interval)", key, re.I) for key in row):
            raise AssertionError("Layer 5 must not derive uncertainty intervals for gaps")
        if row.get("stability") == "suppressed":
            if any(row.get(field) is not None for field in ["absolute_gap", "relative_ratio", "relative_gap_percent"]):
                raise AssertionError("Suppressed Layer 5 raw gaps must remain null")
            if not row.get("suppression_reason"):
                raise AssertionError("Suppressed Layer 5 raw rows require a reason")
            continue
        for field in ["tn_estimate", "comparator_estimate", "absolute_gap"]:
            require_finite(row.get(field), f"Layer 5 raw {field}")
        tolerance = 1e-12 * max(1.0, abs(row["absolute_gap"]))
        if abs(row["absolute_gap"] - (row["tn_estimate"] - row["comparator_estimate"])) > tolerance:
            raise AssertionError("Layer 5 raw gap identity failed")
        if row["is_proportion"]:
            if row.get("relative_ratio") is not None or row.get("relative_gap_percent") is not None:
                raise AssertionError("Layer 5 proportions must not publish relative ratios")
        elif row["comparator_estimate"] > 0:
            require_finite(row.get("relative_ratio"), "Layer 5 raw relative ratio")
            require_finite(row.get("relative_gap_percent"), "Layer 5 raw relative gap")

    raw_by_key = {
        (row["outcome"], row["comparator_id"]): row
        for row in raw_rows
    }
    adjusted_specs = {
        (specification["outcome"], dimension): specification
        for specification in LAYER5_ADJUSTMENT_OUTCOMES
        for dimension in specification["dimensions"]
    }
    adjusted_keys = {
        (row.get("outcome"), row.get("adjustment_dimension"), row.get("comparator_id"))
        for row in adjusted_rows
    }
    expected_adjusted_keys = {
        (outcome, dimension, comparator_id)
        for outcome, dimension in adjusted_specs
        for comparator_id in comparator_ids
    }
    if len(adjusted_keys) != len(adjusted_rows) or adjusted_keys != expected_adjusted_keys:
        raise AssertionError("Layer 5 adjusted outcome/dimension/comparator coverage is incomplete or duplicated")

    classifications = {
        "industry": "project_broad_industry_7",
        "size": "common_size_4",
        "industry_size": "broad_industry_7_x_common_size_4",
    }
    null_when_suppressed = [
        "full_raw_tn", "full_raw_comparator", "full_raw_gap", "common_support_tn",
        "common_support_comparator", "common_support_raw_gap", "standardized_tn",
        "standardized_comparator", "adjusted_gap", "composition_component",
        "within_component", "decomposition_residual",
    ]
    finite_when_stable = [
        *null_when_suppressed, "tn_denominator_coverage", "comparator_denominator_coverage",
    ]
    for row in adjusted_rows:
        dimension = row["adjustment_dimension"]
        specification = adjusted_specs[(row["outcome"], dimension)]
        comparator = comparators[row["comparator_id"]]
        expected_metadata = {
            "survey": specification["survey"],
            "year": "2023-24",
            "outcome_label": specification["label"],
            "unit": specification["unit"],
            "comparator_label": comparator["label"],
            "comparator_type": comparator["type"],
        }
        if any(row.get(field) != expected for field, expected in expected_metadata.items()):
            raise AssertionError(
                f"Layer 5 adjusted metadata drift for {row['outcome']} / "
                f"{dimension} / {row['comparator_id']}"
            )
        if row.get("classification") != classifications[dimension]:
            raise AssertionError("Layer 5 adjusted classification drift")
        expected_cell_count = len(layer5_cell_definitions(pd.DataFrame({
            "nic2": pd.Series(dtype="int64"),
            "size_band": pd.Series(dtype="object"),
        }), dimension))
        if row.get("total_cell_count") != expected_cell_count:
            raise AssertionError("Layer 5 adjusted total-cell count drift")
        if row.get("uncertainty_available") is not False:
            raise AssertionError("Layer 5 adjusted uncertainty must remain unavailable")
        for field in ["tn_denominator_coverage", "comparator_denominator_coverage"]:
            require_finite(row.get(field), f"Layer 5 adjusted {field}")
            if not 0 <= row[field] <= 1:
                raise AssertionError("Layer 5 adjusted denominator coverage must be in [0, 1]")
        if not isinstance(row.get("retained_cell_count"), int) or row["retained_cell_count"] < 0:
            raise AssertionError("Layer 5 adjusted retained-cell count is invalid")
        if row.get("stability") == "suppressed":
            if any(row.get(field) is not None for field in null_when_suppressed):
                raise AssertionError("Suppressed Layer 5 adjusted estimates must remain null")
            if row.get("components") != [] or not row.get("suppression_reason"):
                raise AssertionError("Suppressed Layer 5 adjusted rows require no components and a reason")
            continue
        if row.get("stability") != "stable" or row.get("suppression_reason") is not None:
            raise AssertionError("Layer 5 adjusted stability value is invalid")
        for field in finite_when_stable:
            require_finite(row.get(field), f"Layer 5 adjusted {field}")
        raw = raw_by_key[(row["outcome"], row["comparator_id"])]
        for adjusted_field, raw_field in [
            ("full_raw_tn", "tn_estimate"),
            ("full_raw_comparator", "comparator_estimate"),
            ("full_raw_gap", "absolute_gap"),
        ]:
            if row[adjusted_field] != raw[raw_field]:
                raise AssertionError(f"Layer 5 adjusted {adjusted_field} drift")
        if row["tn_denominator_coverage"] < LAYER5_MIN_COVERAGE or row["comparator_denominator_coverage"] < LAYER5_MIN_COVERAGE:
            raise AssertionError("Layer 5 adjusted denominator support is below threshold")
        if not isinstance(row.get("retained_cell_count"), int) or row["retained_cell_count"] < 2:
            raise AssertionError("Layer 5 adjusted rows require at least two retained cells")
        components = row.get("components")
        if not isinstance(components, list) or len(components) != row["retained_cell_count"]:
            raise AssertionError("Layer 5 adjusted component count drift")
        component_fields = [
            "tn_cell_rate", "comparator_cell_rate", "tn_weight", "comparator_weight",
            "common_weight", "cell_composition_component", "cell_within_component",
        ]
        for component in components:
            for field in component_fields:
                require_finite(component.get(field), f"Layer 5 component {field}")
            for field in ["tn_weight", "comparator_weight", "common_weight"]:
                if not 0 <= component[field] <= 1:
                    raise AssertionError(f"Layer 5 component {field} must be in [0, 1]")
            require_close(
                component["common_weight"],
                0.5 * (component["tn_weight"] + component["comparator_weight"]),
                "component common weight",
            )
            require_close(
                component["cell_composition_component"],
                0.5
                * (component["tn_weight"] - component["comparator_weight"])
                * (component["tn_cell_rate"] + component["comparator_cell_rate"]),
                "cell composition component",
            )
            require_close(
                component["cell_within_component"],
                component["common_weight"]
                * (component["tn_cell_rate"] - component["comparator_cell_rate"]),
                "cell within component",
            )
        for field in ["tn_weight", "comparator_weight", "common_weight"]:
            if abs(math.fsum(component[field] for component in components) - 1.0) > 1e-9:
                raise AssertionError(f"Layer 5 {field} values must sum to one")
        derived_values = {
            "common_support_tn": math.fsum(
                component["tn_weight"] * component["tn_cell_rate"]
                for component in components
            ),
            "common_support_comparator": math.fsum(
                component["comparator_weight"] * component["comparator_cell_rate"]
                for component in components
            ),
            "standardized_tn": math.fsum(
                component["common_weight"] * component["tn_cell_rate"]
                for component in components
            ),
            "standardized_comparator": math.fsum(
                component["common_weight"] * component["comparator_cell_rate"]
                for component in components
            ),
            "composition_component": math.fsum(
                component["cell_composition_component"] for component in components
            ),
            "within_component": math.fsum(
                component["cell_within_component"] for component in components
            ),
        }
        derived_values["common_support_raw_gap"] = (
            derived_values["common_support_tn"]
            - derived_values["common_support_comparator"]
        )
        derived_values["adjusted_gap"] = (
            derived_values["standardized_tn"]
            - derived_values["standardized_comparator"]
        )
        for field, expected in derived_values.items():
            require_close(row[field], expected, field.replace("_", " "))
        tolerance = 1e-8 * max(1.0, abs(row["common_support_raw_gap"]))
        if abs(row["adjusted_gap"] - row["within_component"]) > tolerance:
            raise AssertionError("Layer 5 adjusted-gap identity failed tolerance")
        if abs(row["common_support_raw_gap"] - row["composition_component"] - row["within_component"]) > tolerance:
            raise AssertionError("Layer 5 decomposition identity failed tolerance")
        if abs(row["decomposition_residual"]) > tolerance:
            raise AssertionError("Layer 5 decomposition residual failed tolerance")

    if len(checks) != 28 or any(check.get("status") != "pass" for check in checks):
        raise AssertionError("Publication requires exactly 28 passing legacy validation gates")

    identifier_pattern = re.compile(
        r"^(?:(?:respondent|household|person)(?:$|_(?:id|identifier|serial(?:_no)?|"
        r"no|key|link(?:age)?|hash|uuid))|(?:fsu|psu)(?:$|_(?:serial(?:_no)?|id|code|no))|"
        r"district(?:$|_(?:code|id|identifier|serial(?:_no)?|no))|dispatch.*(?:serial|_id|"
        r"_identifier|_no)|dsl|sample_est(?:ablishment)?(?:$|_(?:id|identifier|serial(?:_no)?|"
        r"no))|.*_design)$",
        re.I,
    )

    def reject_identifier_keys(value) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if identifier_pattern.search(str(key)):
                    raise AssertionError(f"Prohibited identifier field exported: {key}")
                reject_identifier_keys(item)
        elif isinstance(value, list):
            for item in value:
                reject_identifier_keys(item)

    reject_identifier_keys(structure_v1)


def outcome_rows(
    frame: pd.DataFrame,
    survey: str,
    numerator: str,
    denominator: str,
    per_person_label: str,
    value_field: str,
    share_field: str,
    sample_unit: str,
    size_specs: list[tuple[str, str, str]],
    concept: str | None = None,
    gva_column: str | None = None,
) -> list[dict]:
    rows: list[dict] = []

    def append_cell(group: pd.DataFrame, geography: tuple[str, str, str], dimension: str, **labels) -> None:
        geography_id, geography_label, geography_type = geography
        quality = outcome_cell(group, numerator, denominator)
        row = {
            "survey": survey,
            "year": "2023-24",
            "dimension": dimension,
            "geography_id": geography_id,
            "geography_label": geography_label,
            "geography_type": geography_type,
            "sample_unit": sample_unit,
            "per_person_label": per_person_label,
            **labels,
            **quality,
            "denominator_positive": quality["_denominator_total"] > 0,
            value_field: (
                quality["_numerator_total"] / quality["_denominator_total"]
                if quality["stability"] == "stable" and quality["_denominator_total"] > 0
                else None
            ),
            share_field: None,
        }
        if concept is not None:
            row["concept"] = concept
        if gva_column is not None:
            weighted_gva = group[gva_column].fillna(0.0) * group["weight"]
            absolute_gva = weighted_gva.abs()
            gva_total = float(weighted_gva.sum())
            gva_concentration = (
                float(absolute_gva.max() / absolute_gva.sum()) if absolute_gva.sum() > 0 else 0.0
            )
            row["aggregate_gva_positive"] = gva_total > 0
            row["labour_cost_proxy_share_of_gva"] = (
                quality["_numerator_total"] / gva_total
                if quality["stability"] == "stable"
                and gva_total > 0
                and gva_concentration <= MAX_EMPLOYMENT_CONCENTRATION
                else None
            )
        rows.append(row)

    for geography_id, geography_label, geography_type, geography_frame in geography_groups(frame):
        geography = (geography_id, geography_label, geography_type)
        eligible = geography_frame.loc[geography_frame["_outcome_eligible"]]
        append_cell(eligible, geography, "overall")
        for classification, classification_label, band_column in size_specs:
            for band in SIZE_BANDS:
                append_cell(
                    eligible.loc[eligible[band_column].eq(band["id"])],
                    geography,
                    "size",
                    classification=classification,
                    classification_label=classification_label,
                    size_band=band["id"],
                    size_band_label=band["label"],
                )
            if frame[band_column].eq("zero-unclassified").any():
                append_cell(
                    eligible.loc[eligible[band_column].eq("zero-unclassified")],
                    geography,
                    "size",
                    classification=classification,
                    classification_label=classification_label,
                    size_band="zero-unclassified",
                    size_band_label="Below 1 / zero / unclassified",
                )

    industry_geographies = [TN, *PEER_CODES, *SENSITIVITY_CODES]
    for geography_id, geography_label, geography_type, geography_frame in geography_groups(
        frame, industry_geographies
    ):
        geography = (geography_id, geography_label, geography_type)
        eligible = geography_frame.loc[geography_frame["_outcome_eligible"]]
        for nic2, industry_label in NIC2.items():
            append_cell(
                eligible.loc[eligible["nic2"].eq(nic2)],
                geography,
                "industry",
                nic2=nic2,
                industry_label=industry_label,
            )

    group_fields = ["survey", "dimension", "geography_id"]
    if concept is not None:
        group_fields.append("concept")
    groups: dict[tuple, list[dict]] = {}
    for row in rows:
        if row["dimension"] == "overall":
            continue
        key = tuple(row[field] for field in group_fields)
        if row["dimension"] == "size":
            key += (row["classification"],)
        groups.setdefault(key, []).append(row)
    for siblings in groups.values():
        total = sum(row["_numerator_total"] for row in siblings)
        if total and all(row["stability"] == "stable" for row in siblings):
            for row in siblings:
                row[share_field] = row["_numerator_total"] / total
    for row in rows:
        row.pop("_numerator_total")
        row.pop("_denominator_total")
    return rows


def asi_structure_frame() -> pd.DataFrame:
    with zipfile.ZipFile(ASI_2023_ZIP) as archive:
        block_a = read_block(archive, "A")
        block_e = read_block(archive, "E")

    columns = list(block_a.columns)
    state_col = pick_column(columns, ("statecode", "statecd", "a7", "aitm7"), ("state",))
    nic_col = pick_column(columns, ("nic5digit", "inc5digit", "indcd", "indcdreturn", "a5", "aitm5"), ("nic5",))
    status_col = pick_column(columns, ("statusofunit", "unitstatus", "a12", "aitm12"), ("status",))
    weight_col = pick_column(columns, ("wgt", "weight", "mult", "multiplier", "multilplier"), ("mult",))
    units_col = pick_column(columns, ("noofunits", "a11", "aitm11"), ("noofunit",))
    required = {"state": state_col, "nic": nic_col, "status": status_col, "weight": weight_col}
    missing = [name for name, column in required.items() if column is None]
    if missing:
        raise ValueError(f"ASI 2023-24 Block A missing fields: {missing}")

    frame = pd.DataFrame({
        "dsl": string_values(block_a[dsl_column(block_a, "A")]),
        "state": string_values(block_a[state_col]).str.zfill(2),
        "nic5": string_values(block_a[nic_col]).str.replace(r"\D", "", regex=True).str.zfill(5),
        "status": pd.to_numeric(block_a[status_col], errors="coerce"),
        "weight": numeric(block_a[weight_col]),
        "reported_units": numeric(block_a[units_col]) if units_col else 1.0,
    }).drop_duplicates("dsl")
    employment = employment_values(block_e, 2023)[[
        "dsl", "employees", "workers", "supervisory_workers", "other_employees",
        "unpaid_family_members",
    ]]
    frame = frame.merge(employment, on="dsl", how="left", validate="one_to_one")
    for column in employment.columns.drop("dsl"):
        frame[column] = numeric(frame[column], frame.index)
    frame["paid_persons_engaged"] = (
        frame["workers"] + frame["supervisory_workers"] + frame["other_employees"]
    )
    frame["nic2"] = pd.to_numeric(frame["nic5"].str[:2], errors="coerce")
    frame = frame.loc[frame["status"].isin([1, 2, 3]) & frame["nic2"].between(10, 33)].copy()
    if frame["weight"].le(0).any() or frame["reported_units"].le(0).any():
        raise ValueError("Retained ASI manufacturing returns must have positive weights and reported-unit counts")

    outcomes = build_factory_frame(ASI_2023_ZIP, 2023)[
        ["dsl", "gva", "emoluments", "compensation_employees"]
    ]
    frame = frame.merge(outcomes, on="dsl", how="left", validate="one_to_one")
    if frame[["gva", "emoluments", "compensation_employees"]].isna().any().any():
        raise ValueError("ASI outcome reconstruction is missing retained manufacturing returns")
    return frame


def size_distribution(
    frame: pd.DataFrame,
    survey: str,
    classification: str,
    classification_label: str,
    sample_unit: str,
    include_zero: bool = False,
) -> list[dict]:
    rows = []
    bands = [*(SIZE_BANDS), *([{"id": "zero-unclassified", "label": "Below 1 / zero / unclassified"}] if include_zero else [])]
    for geography_id, geography_label, geography_type, geography in geography_groups(frame):
        unit_total = float(geography["unit_contribution"].sum())
        employment_total = float(geography["employment_contribution"].sum())
        for band in bands:
            group = geography.loc[geography["size_band"].eq(band["id"])]
            quality = cell_quality(group)
            unit_measure = (
                "establishments" if survey == "asuse"
                else "reported units classified by sample-return employment"
                if classification == "per_return_sensitivity"
                else "reported units"
            )
            row = {
                "survey": survey, "year": "2023-24", "geography_id": geography_id,
                "geography_label": geography_label, "geography_type": geography_type,
                "classification": classification, "classification_label": classification_label,
                "size_band": band["id"], "size_band_label": band["label"],
                "sample_unit": sample_unit, "unit_measure": unit_measure,
                "employment_measure": "workers" if survey == "asuse" else "persons engaged",
                **quality,
                "estimated_units": float(group["unit_contribution"].sum()),
                "unit_share": float(group["unit_contribution"].sum() / unit_total) if unit_total else math.nan,
                "estimated_employment": float(group["employment_contribution"].sum()),
                "employment_share": float(group["employment_contribution"].sum() / employment_total) if employment_total else math.nan,
            }
            rows.append(suppress_unstable(row, ("estimated_units", "unit_share", "estimated_employment", "employment_share")))
    return rows


def middle_diagnostics(size_rows: list[dict]) -> list[dict]:
    diagnostics = []
    keys = {(row["survey"], row["geography_id"], row["classification"]) for row in size_rows}
    for survey, geography_id, classification in sorted(keys):
        group = [row for row in size_rows if (row["survey"], row["geography_id"], row["classification"]) == (survey, geography_id, classification)]
        for definition in MIDDLE_DEFINITIONS:
            cells = [row for row in group if row["size_band"] in definition["size_bands"]]
            unavailable = len(cells) != len(definition["size_bands"]) or any(row["stability"] != "stable" for row in cells)
            reason = "one or more constituent size bands are suppressed" if unavailable else None
            first = group[0]
            row = {
                "survey": survey, "year": "2023-24", "geography_id": geography_id,
                "geography_label": first["geography_label"], "geography_type": first["geography_type"],
                "classification": classification, "classification_label": first["classification_label"],
                "middle_definition": definition["id"], "middle_definition_label": definition["label"],
                "sample_unit": first["sample_unit"],
                "unit_measure": first["unit_measure"],
                "employment_measure": first["employment_measure"],
                "sample_count": sum(cell["sample_count"] for cell in cells),
                "stability": "suppressed" if unavailable else "stable", "suppression_reason": reason,
                "estimated_units": None if unavailable else sum(cell["estimated_units"] for cell in cells),
                "unit_share": None if unavailable else sum(cell["unit_share"] for cell in cells),
                "estimated_employment": None if unavailable else sum(cell["estimated_employment"] for cell in cells),
                "employment_share": None if unavailable else sum(cell["employment_share"] for cell in cells),
            }
            diagnostics.append(row)
    return diagnostics


def industry_employment(frame: pd.DataFrame, survey: str, sample_unit: str, size_cross: bool = False) -> list[dict]:
    rows = []
    bands = [*SIZE_BANDS, {"id": "zero-unclassified", "label": "Below 1 / zero / unclassified"}]
    for geography_id, geography_label, geography_type, geography in geography_groups(frame, [TN]):
        employment_total = float(geography["employment_contribution"].sum())
        for nic2, nic_label in NIC2.items():
            industry = geography.loc[geography["nic2"].eq(nic2)]
            selected_bands = bands if size_cross and survey == "asi" else SIZE_BANDS if size_cross else [None]
            for band in selected_bands:
                group = industry if band is None else industry.loc[industry["size_band"].eq(band["id"])]
                quality = cell_quality(group)
                row = {
                    "survey": survey, "year": "2023-24", "geography_id": geography_id,
                    "geography_label": geography_label, "geography_type": geography_type,
                    "nic2": nic2, "industry_label": nic_label, "sample_unit": sample_unit,
                    "employment_measure": "workers" if survey == "asuse" else "persons engaged",
                    **quality,
                    "estimated_employment": float(group["employment_contribution"].sum()),
                    "employment_share": float(group["employment_contribution"].sum() / employment_total) if employment_total else math.nan,
                }
                if band is not None:
                    row.update(size_band=band["id"], size_band_label=band["label"])
                rows.append(suppress_unstable(row, ("estimated_employment", "employment_share")))
    return rows


def plfs_enterprise_size(frame: pd.DataFrame) -> list[dict]:
    rows = []
    labels = {1: "Fewer than 6", 2: "6-9", 3: "10-19", 4: "20+", 9: "Unknown"}
    manufacturing = frame.loc[frame["manufacturing"]].copy()
    manufacturing["enterprise_size_code"] = pd.to_numeric(manufacturing["enterprise_size_code"], errors="coerce").astype("Int64")
    manufacturing["employment_contribution"] = manufacturing["weight"]
    for geography_id, geography_label, geography_type, geography in geography_groups(
        manufacturing, [TN, *PEER_CODES, *SENSITIVITY_CODES]
    ):
        total = float(geography["employment_contribution"].sum())
        for code, label in labels.items():
            group = geography.loc[geography["enterprise_size_code"].eq(code)]
            quality = cell_quality(group)
            row = {
                "survey": "plfs", "year": "2023-24", "geography_id": geography_id,
                "geography_label": geography_label, "geography_type": geography_type,
                "size_code": code, "size_label": label, "sample_unit": "sample workers",
                "employment_measure": "usually working persons", **quality,
                "worker_share": float(group["employment_contribution"].sum() / total) if total else math.nan,
            }
            rows.append(suppress_unstable(row, ("worker_share",)))
    return rows


def build_structure_v1(
    asuse: pd.DataFrame,
    asi: pd.DataFrame,
    plfs_frame_data: pd.DataFrame,
    plfs_scaffold: pd.MultiIndex,
    plfs_scaffold_complete: bool,
) -> dict:
    asuse = asuse.copy()
    asuse["nic2"] = pd.to_numeric(asuse["major_nic_2dig"], errors="coerce")
    asuse["size_band"] = size_band(asuse["total_workers"])
    asuse["unit_contribution"] = asuse["weight"]
    asuse["employment_contribution"] = asuse["total_workers"] * asuse["weight"]

    asi = asi.copy()
    asi["unit_contribution"] = asi["weight"] * asi["reported_units"]
    asi["employment_contribution"] = asi["employees"] * asi["weight"]
    asi["equal_allocation_size"] = asi["employees"] / asi["reported_units"].replace(0, np.nan)
    asi["size_band"] = size_band(asi["equal_allocation_size"], include_zero=True)
    asi_primary = size_distribution(
        asi, "asi", "equal_allocation_approximation",
        "Persons engaged / reported units (equal-allocation approximation)", "sample returns", include_zero=True,
    )
    asi["per_return_size_band"] = size_band(asi["employees"], include_zero=True)
    asi_sensitivity = asi.copy()
    asi_sensitivity["size_band"] = asi_sensitivity["per_return_size_band"]

    establishment_size = [
        *size_distribution(
            asuse, "asuse", "reported_establishment_workers",
            "Reported workers in the sampled establishment", "sample establishments",
        ),
        *asi_primary,
        *size_distribution(
            asi_sensitivity, "asi", "per_return_sensitivity",
            "Persons engaged per sample return (classification sensitivity; not factory size)",
            "sample returns", include_zero=True,
        ),
    ]

    asuse_value = asuse.copy()
    asuse_value["_outcome_eligible"] = asuse_value["annual_gva"].notna()
    asi_value = asi.copy()
    asi_value["_outcome_eligible"] = True
    value_addition = [
        *outcome_rows(
            asuse_value, "asuse", "annual_gva", "total_workers",
            "GVA per worker in market establishments", "per_person_value",
            "gva_contribution_share", "sample establishments",
            [("reported_establishment_workers", "Reported workers in the sampled establishment", "size_band")],
        ),
        *outcome_rows(
            asi_value, "asi", "gva", "employees", "GVA per person engaged",
            "per_person_value", "gva_contribution_share", "sample returns",
            [
                ("equal_allocation_approximation", "Persons engaged / reported units (equal-allocation approximation)", "size_band"),
                ("per_return_sensitivity", "Persons engaged per sample return (classification sensitivity; not factory size)", "per_return_size_band"),
            ],
        ),
    ]

    asuse_compensation = asuse.copy()
    asuse_compensation["_outcome_eligible"] = (
        asuse_compensation["est_type"].eq(1) & asuse_compensation["annual_emoluments"].notna()
    )
    asi_compensation = asi.copy()
    asi_compensation["_outcome_eligible"] = True
    compensation_size_specs = [
        ("equal_allocation_approximation", "Persons engaged / reported units (equal-allocation approximation)", "size_band"),
        ("per_return_sensitivity", "Persons engaged per sample return (classification sensitivity; not factory size)", "per_return_size_band"),
    ]
    establishment_compensation = [
        *outcome_rows(
            asuse_compensation, "asuse", "annual_emoluments", "hired_workers",
            "Annual emoluments per hired worker", "per_person_value",
            "compensation_contribution_share", "sample HWE establishments",
            [("reported_establishment_workers", "Reported workers in the sampled establishment", "size_band")],
            concept="annual_emoluments",
        ),
        *outcome_rows(
            asi_compensation, "asi", "emoluments", "paid_persons_engaged",
            "Emoluments per paid person engaged", "per_person_value",
            "compensation_contribution_share", "sample returns", compensation_size_specs,
            concept="emoluments",
        ),
        *outcome_rows(
            asi_compensation, "asi", "compensation_employees", "paid_persons_engaged",
            "Labour-cost proxy per paid person engaged", "per_person_value",
            "compensation_contribution_share", "sample returns", compensation_size_specs,
            concept="labour_cost_proxy", gva_column="gva",
        ),
    ]
    worker_earnings = plfs_worker_earnings(
        plfs_frame_data, plfs_scaffold, plfs_scaffold_complete
    )
    worker_job_quality = plfs_worker_job_quality(
        plfs_frame_data, plfs_scaffold, plfs_scaffold_complete
    )
    peer_comparisons_raw_rows = peer_comparisons_raw({
        "value_addition": value_addition,
        "establishment_compensation": establishment_compensation,
        "worker_earnings": worker_earnings,
        "worker_job_quality": worker_job_quality,
    })
    peer_comparisons_adjusted_rows = peer_comparisons_adjusted(
        {
            "gva_per_worker": asuse_value.loc[asuse_value["_outcome_eligible"]],
            "annual_emoluments_per_hired_worker": asuse_compensation.loc[asuse_compensation["_outcome_eligible"]],
            "gva_per_person_engaged": asi_value.loc[asi_value["_outcome_eligible"]],
            "emoluments_per_paid_person_engaged": asi_compensation.loc[asi_compensation["_outcome_eligible"]],
            "labour_cost_proxy_per_paid_person_engaged": asi_compensation.loc[asi_compensation["_outcome_eligible"]],
        },
        peer_comparisons_raw_rows,
    )
    return {
        "metadata": {
            "version": "1.0", "reference_year": "2023-24", "manufacturing_nic2": {"minimum": 10, "maximum": 33},
            "geography_note": "ASUSE and ASI include India and every available State/UT. PLFS Layer 4 overall rows do the same; PLFS subgroup rows cover India, Tamil Nadu, Gujarat, Maharashtra, Karnataka, Telangana and Kerala.",
            "peers": [{"code": code, "label": STATE_LABELS[code]} for code in PEER_CODES],
            "sensitivity_geographies": [{"code": code, "label": STATE_LABELS[code]} for code in SENSITIVITY_CODES],
            "asi_primary_size_measure": "Persons engaged divided by reported units; all reported units on a return are assigned the same equal-allocation size. Values below one are unclassified because this average is not an observed unit size.",
            "asi_sensitivity": "Persons engaged per sample return; this is a classification sensitivity, not a count of factories by observed factory size.",
            "plfs_role": "Worker-side cross-check only; it is not reconciled to ASUSE or ASI.",
            "layer3": {
                "price_basis": "Current rupees.",
                "scope": "ASUSE market-establishment GVA and HWE emoluments remain separate from ASI registered-factory outcomes.",
                "dimensions": "Overall and size cover India and all available States/UTs; industry covers India, Tamil Nadu, Gujarat, Maharashtra, Karnataka, Telangana and Kerala. No size-by-industry outcomes are produced.",
                "asuse_denominators": {
                    "value_addition": "Total workers in market establishments with Level 08 item 769.",
                    "compensation": "Hired-worker emolument components (Level 10 items 902, 903, 912 and 929) divided by formal plus informal hired workers (Level 09 items 782 and 783) in HWE establishments; working-owner items 901 and 911 are excluded to match the denominator.",
                },
                "asi_denominators": {
                    "value_addition": "Total persons engaged (Block E row 10).",
                    "compensation": "Paid persons engaged: workers plus supervisory staff plus other employees (Block E rows 6, 7 and 8).",
                },
                "asi_labour_cost_proxy": "Emoluments plus provident-fund contribution and workmen/staff welfare. Welfare is not necessarily cash pay.",
            },
            "plfs_enterprise_size_fields": {
                "principal": "b5pt1q10_perv1",
                "subsidiary": "b5pt2q9_perv1",
                "selection": "Use principal particulars when principal status is employed; otherwise use subsidiary particulars.",
                "codes": {"1": "Fewer than 6", "2": "6-9", "3": "10-19", "4": "20+", "9": "Unknown"},
            },
            "layer4": {
                "earnings_activity_concept": "Current weekly status, using Block 6 manufacturing earning activities. Regular monthly, self-employment 30-day gross and casual person-day earnings remain separate.",
                "job_quality_activity_concept": "Usual-status regular wage/salaried manufacturing workers, with employed principal-activity precedence and subsidiary particulars only when principal status is not employed.",
                "sex_convention": "Male follows the official PLFS convention and combines sex codes 1 and 3; female is code 2.",
                "dimensions": "Overall rows cover India and all available States/UTs. Sex and sector rows cover India, Tamil Nadu, Gujarat, Maharashtra, Karnataka, Telangana and Kerala; job quality also includes enterprise size for those geographies. Earnings by enterprise size are not produced.",
                "uncertainty": "Official two-interpenetrating-subsample ratio variance using the complete full-person-file design-stratum/subsample scaffold before domain filtering. Proportion intervals are clipped to 0-1; positive-earnings lower bounds are clipped to zero.",
                "suppression": "Suppress below 30 valid positive-weight denominator observations, 10 active FSUs or Kish effective n of 30; above 20% denominator-weight or absolute earnings concentration; when paired-subsample variance is unavailable; above 30% RSE; or, for rates, below 10 sampled outcomes or non-outcomes. Stable RSE is at most 20%; low precision is above 20% and at most 30%. Social-security categories are assessed independently so a rare unknown category does not suppress the official no-benefit headline.",
            },
            "layer5": {
                "question": "Whether aggregate Tamil Nadu peer gaps are associated with industrial or establishment-size composition, or remain under a common composition.",
                "interpretation_boundary": "Raw and adjusted comparisons are descriptive. They are not causal effects of industry, establishment size, policy, productivity, formalisation or firm growth; ASUSE, ASI and PLFS remain separate statistical universes.",
                "comparators": LAYER5_COMPARATORS,
                "raw_gap_method": "Absolute gaps equal Tamil Nadu minus comparator. Rupee outcomes also report Tamil Nadu/comparator ratios and 100 times ratio minus one; proportions report differences in proportion units for percentage-point display and no ratio.",
                "industry_classification": {
                    "id": "project_broad_industry_7",
                    "groups": LAYER5_INDUSTRY_GROUPS,
                    "note": "Project analytical support groups, not an official NIC aggregation.",
                },
                "size_classification": {
                    "id": "common_size_4",
                    "groups": LAYER5_SIZE_GROUPS,
                    "asi_basis": "Primary equal-allocation approximation only; zero-unclassified records remain in the full denominator and are uncovered by size adjustment.",
                },
                "adjustment_method": "Pairwise symmetric standardisation. Each geography's outcome-specific denominator weights are renormalised over jointly stable common cells; the common weight is the average of the Tamil Nadu and comparator weights.",
                "support_gate": "Publish only when at least two jointly stable positive-denominator cells cover at least 95% of each geography's full eligible outcome denominator and both decomposition identities pass tolerance.",
                "omitted_adjustments": "No PLFS adjustment, no ASUSE industry-by-size adjustment, and no adjustment of ASI labour-cost-proxy share of GVA.",
                "uncertainty_available": False,
                "uncertainty_note": "Layer 3 does not provide design-based variances for ASUSE or ASI outcome cells, so adjusted estimates, gaps and components have no confidence intervals or significance tests in v1.",
            },
        },
        "size_bands": SIZE_BANDS,
        "middle_definitions": MIDDLE_DEFINITIONS,
        "establishment_size": establishment_size,
        "middle_diagnostic": middle_diagnostics(establishment_size),
        "industry_employment": [
            *industry_employment(asuse, "asuse", "sample establishments"),
            *industry_employment(asi, "asi", "sample returns"),
        ],
        "size_industry_employment": [
            *industry_employment(asuse, "asuse", "sample establishments", size_cross=True),
            *industry_employment(asi, "asi", "sample returns", size_cross=True),
        ],
        "plfs_enterprise_size": plfs_enterprise_size(plfs_frame_data),
        "value_addition": value_addition,
        "establishment_compensation": establishment_compensation,
        "worker_earnings": worker_earnings,
        "worker_job_quality": worker_job_quality,
        "peer_comparisons_raw": peer_comparisons_raw_rows,
        "peer_comparisons_adjusted": peer_comparisons_adjusted_rows,
        "quality": {
            "allowed_surveys": sorted(SURVEYS), "allowed_stability": sorted(STABILITY),
            "minimum_sample_count": MIN_SAMPLE,
            "maximum_largest_weighted_employment_contribution": MAX_EMPLOYMENT_CONCENTRATION,
            "suppression_rule": "Suppress structural cells with fewer than 10 sampled units/workers or with one record contributing more than 70% of weighted employment. Suppressed estimates and shares are null; labels, counts, and reasons remain.",
            "outcome_suppression_rule": "Suppress outcome ratios when sample count is below 10 or one record exceeds 70% of the weighted denominator or absolute weighted numerator. Contribution shares are published only when every sibling is stable; non-positive ratio denominators return null.",
            "worker_suppression_rule": "Layer 4 uses the separate PLFS hard-suppression and design-based precision rules stated in metadata.layer4.suppression.",
            "sample_units": {"asuse": "sample establishments", "asi": "sample returns", "plfs": "persons or person-days, depending on the Layer 4 concept"},
        },
    }


def plfs_layer4_validation_values(
    frame: pd.DataFrame,
    worker_earnings: list[dict],
    scaffold: pd.MultiIndex,
    scaffold_complete: bool,
) -> dict:
    nic = pd.to_numeric(frame["nic"], errors="coerce")
    nonagricultural_regular = frame.loc[
        frame["usual_employed"] & frame["status"].eq(31) & nic.between(5_000, 99_999)
    ].copy()
    table36 = {}
    specifications = {
        "no_written_contract": ("contract_code", {1, 2, 3, 4}, {1}),
        "no_paid_leave": ("paid_leave_code", {1, 2}, {2}),
        "no_social_security": ("social_security_code", set(range(1, 10)), {8}),
    }
    for geography_id in ["IN", TN]:
        geography = (
            nonagricultural_regular if geography_id == "IN"
            else nonagricultural_regular.loc[nonagricultural_regular["state"].eq(geography_id)]
        )
        table36[geography_id] = {}
        for concept, (field, denominator_codes, numerator_codes) in specifications.items():
            codes = pd.to_numeric(geography[field], errors="coerce")
            valid = geography.loc[codes.isin(denominator_codes)]
            valid_codes = codes.loc[valid.index]
            table36[geography_id][concept] = weighted_share(
                valid, valid_codes.isin(numerator_codes)
            )

    nonagricultural_workers = frame.loc[
        frame["usual_employed"] & nic.between(5_000, 99_999)
    ].copy()
    enterprise_size = pd.to_numeric(
        nonagricultural_workers["enterprise_size_code"], errors="coerce"
    ).astype("Int64")
    valid_size = nonagricultural_workers.loc[enterprise_size.isin([1, 2, 3, 4, 9])]
    valid_size_codes = enterprise_size.loc[valid_size.index]
    table37 = {
        "shares": {
            code: weighted_share(valid_size, valid_size_codes.eq(code))
            for code in [1, 2, 3, 4, 9]
        },
        "sample_total": int(len(valid_size)),
    }

    casual_india = next(
        row for row in worker_earnings
        if row["concept"] == "casual_person_day_earnings"
        and row["dimension"] == "overall"
        and row["geography_id"] == "IN"
    )
    if casual_india["estimate"] is None:
        raise AssertionError("PLFS Table 51 validation cell was suppressed")

    rural_tn = frame.loc[
        frame["usual_employed"]
        & frame["state"].eq(TN)
        & frame["sector_category"].eq("rural")
    ].copy()
    rural_tn["_value"] = rural_tn["manufacturing"].astype(float)
    rural_design = plfs_estimate_cell(
        rural_tn, scaffold, scaffold_complete, binary=True
    )
    if rural_design["estimate"] is None or rural_design["rse"] is None:
        raise AssertionError("PLFS TN rural manufacturing design check was suppressed")

    return {
        "table36": table36,
        "table37": table37,
        "table51": {
            "manufacturing_casual_earnings": casual_india["estimate"],
            "sample_person_days": casual_india["sample_count"],
        },
        "tn_rural_manufacturing": {
            "share_percent": 100.0 * rural_design["estimate"],
            "rse_percent": 100.0 * rural_design["rse"],
        },
    }


def assert_absolute_close(
    name: str,
    actual: float,
    expected: float,
    absolute_tolerance: float,
    tolerance_basis: str,
) -> dict:
    if not math.isfinite(actual):
        raise AssertionError(f"{name}: reconstructed value is not finite")
    absolute_error = abs(actual - expected)
    if absolute_error > absolute_tolerance:
        raise AssertionError(
            f"{name}: reconstructed {actual:,.6f}, published {expected:,.6f}, "
            f"absolute error {absolute_error:,.6f} exceeds {absolute_tolerance:,.6f}"
        )
    return {
        "check": name,
        "reconstructed": actual,
        "published": expected,
        "absolute_error": absolute_error,
        "tolerance": absolute_tolerance,
        "tolerance_basis": tolerance_basis,
        "status": "pass",
    }


def assert_exact(name: str, actual: int, expected: int) -> dict:
    if actual != expected:
        raise AssertionError(f"{name}: reconstructed {actual:,}, published {expected:,}")
    return {
        "check": name,
        "reconstructed": actual,
        "published": expected,
        "absolute_error": 0,
        "tolerance": 0,
        "tolerance_basis": "Published unweighted sample count; exact match required.",
        "status": "pass",
    }


def assert_close(name: str, actual: float, expected: float, relative_tolerance: float) -> dict:
    if not math.isfinite(actual):
        raise AssertionError(f"{name}: reconstructed value is not finite")
    relative_error = abs(actual - expected) / expected
    if relative_error > relative_tolerance:
        raise AssertionError(
            f"{name}: reconstructed {actual:,.4f}, published {expected:,.4f}, "
            f"relative error {relative_error:.3%} exceeds {relative_tolerance:.3%}"
        )
    return {
        "check": name,
        "reconstructed": actual,
        "published": expected,
        "relative_error": relative_error,
        "tolerance": relative_tolerance,
        "status": "pass",
    }


def json_safe(value):
    """Convert numpy scalars and non-finite estimates to JSON-safe values."""
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, (np.integer, np.floating)):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def main() -> int:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    SITE_DATA.parent.mkdir(parents=True, exist_ok=True)

    asuse_all_states = asuse_frame()
    asuse_all = asuse_all_states.loc[asuse_all_states["state"].eq(TN)].copy()
    asuse = asuse_all.loc[asuse_all["major_nic_2dig"].between(10, 33)].copy()
    asuse["establishment_unit"] = 1.0
    asuse_sectors, asuse_tiers = summarize_asuse(asuse)
    for tier_key in ("oae", "hwe"):
        asuse_tiers[tier_key]["reconstructed_gva_per_worker"] = asuse_tiers[tier_key]["gva_per_worker"]
        asuse_tiers[tier_key]["gva_per_worker"] = PUBLISHED["asuse"][f"{tier_key}_productivity"]
    plfs_all = plfs_frame()
    plfs = plfs_summary(plfs_all)
    asi_tier, asi_sectors = asi_summary()
    asuse_structure = asuse_all_states.loc[asuse_all_states["major_nic_2dig"].between(10, 33)].copy()
    asi_structure = asi_structure_frame()
    plfs_scaffold, plfs_scaffold_complete = plfs_design_scaffold(plfs_all)
    structure_v1 = build_structure_v1(
        asuse_structure,
        asi_structure,
        plfs_all,
        plfs_scaffold,
        plfs_scaffold_complete,
    )
    layer4_validation = plfs_layer4_validation_values(
        plfs_all,
        structure_v1["worker_earnings"],
        plfs_scaffold,
        plfs_scaffold_complete,
    )
    all_ratio, all_ratio_rse = ratio_rse(
        asuse_all,
        asuse_all["major_nic_5dig"].ne(68_108),
    )
    manufacturing_ratio, manufacturing_ratio_rse = ratio_rse(
        asuse_all,
        asuse_all["major_nic_2dig"].between(10, 33),
    )

    hwe_outcomes = asuse_structure.loc[
        asuse_structure["state"].eq(TN) & asuse_structure["est_type"].eq(1)
    ]
    reconstructed_hired_workers = float(
        (hwe_outcomes["hired_workers"] * hwe_outcomes["weight"]).sum()
    )
    reconstructed_emoluments_per_hired_worker = weighted_ratio(
        hwe_outcomes, "annual_emoluments", "hired_workers"
    )

    checks = []
    for key, published_key in [("oae", "oae_establishments"), ("hwe", "hwe_establishments")]:
        checks.append(assert_close(
            f"ASUSE TN manufacturing {key.upper()} establishments",
            asuse_tiers[key]["estimated_establishments"],
            PUBLISHED["asuse"][published_key],
            0.001,
        ))
    checks.append(assert_close(
        "ASUSE TN manufacturing hired workers",
        reconstructed_hired_workers,
        PUBLISHED["asuse"]["hired_workers"],
        0.001,
    ))
    checks.append(assert_close(
        "ASUSE TN manufacturing annual emoluments per hired worker",
        reconstructed_emoluments_per_hired_worker,
        PUBLISHED["asuse"]["annual_emoluments_per_hired_worker"],
        0.01,
    ))
    for key, published_key in [("oae", "oae_productivity"), ("hwe", "hwe_productivity")]:
        checks.append(assert_close(
            f"ASUSE TN manufacturing {key.upper()} GVA per worker",
            asuse_tiers[key]["reconstructed_gva_per_worker"],
            PUBLISHED["asuse"][published_key],
            0.01,
        ))
    for key in [
        "manufacturing_share", "male_manufacturing_share", "female_manufacturing_share",
        "rural_manufacturing_share", "urban_manufacturing_share",
    ]:
        checks.append(assert_close(
            f"PLFS TN {key.replace('_', ' ')}",
            plfs[key], PUBLISHED["plfs"][key], 0.005,
        ))
    checks.append(assert_close(
        "ASUSE TN all-activity GVA-per-worker RSE",
        all_ratio_rse, 2.64, 0.15,
    ))

    one_decimal_percentage_tolerance = 0.000500001
    for geography_id, geography_label in [("IN", "India"), (TN, "Tamil Nadu")]:
        for concept, label in [
            ("no_written_contract", "no written contract"),
            ("no_paid_leave", "no paid leave"),
            ("no_social_security", "no social security"),
        ]:
            checks.append(assert_absolute_close(
                f"PLFS Table 36 {geography_label} {label}",
                layer4_validation["table36"][geography_id][concept],
                PUBLISHED["plfs"]["table36"][geography_id][concept],
                one_decimal_percentage_tolerance,
                "Published to one decimal percentage point; tolerance is half the displayed unit.",
            ))
    for code, expected in PUBLISHED["plfs"]["table37"]["shares"].items():
        checks.append(assert_absolute_close(
            f"PLFS Table 37 enterprise size {code} share",
            layer4_validation["table37"]["shares"][code],
            expected,
            one_decimal_percentage_tolerance,
            "Published to one decimal percentage point; tolerance is half the displayed unit.",
        ))
    checks.append(assert_exact(
        "PLFS Table 37 sample total",
        layer4_validation["table37"]["sample_total"],
        PUBLISHED["plfs"]["table37"]["sample_total"],
    ))
    checks.append(assert_absolute_close(
        "PLFS Table 51 manufacturing casual earnings",
        layer4_validation["table51"]["manufacturing_casual_earnings"],
        PUBLISHED["plfs"]["table51"]["manufacturing_casual_earnings"],
        0.500001,
        "Published to the nearest rupee; tolerance is half the displayed unit.",
    ))
    checks.append(assert_exact(
        "PLFS Table 51 manufacturing casual earnings sample person-days",
        layer4_validation["table51"]["sample_person_days"],
        PUBLISHED["plfs"]["table51"]["sample_person_days"],
    ))
    checks.append(assert_absolute_close(
        "PLFS TN rural manufacturing share paired-subsample check",
        layer4_validation["tn_rural_manufacturing"]["share_percent"],
        PUBLISHED["plfs"]["rural_manufacturing_share"],
        0.005000001,
        "Published to 0.01 percentage point; tolerance is half the displayed unit.",
    ))
    checks.append(assert_absolute_close(
        "PLFS TN rural manufacturing share RSE",
        layer4_validation["tn_rural_manufacturing"]["rse_percent"],
        PUBLISHED["plfs"]["rural_manufacturing_rse"],
        0.005000001,
        "Published to 0.01 percentage point; tolerance is half the displayed unit.",
    ))

    output = {
        "meta": {
            "title": "Tamil Nadu Manufacturing: A Structural Snapshot",
            "built_from": ["ASUSE 2023-24", "ASI 2023-24", "PLFS 2023-24"],
            "price_basis": "Current rupees; no time-series growth claim is made.",
            "comparison_warning": (
                "The three surveys cover different statistical units and overlapping but non-identical "
                "reference periods. Comparisons diagnose structure; they do not track firm transitions."
            ),
            "disclosure": "Public outputs include weighted aggregates, labels, unweighted sample counts, validation results and disclosure flags, but no respondent-level records or linkage identifiers.",
        },
        "headline": {
            "unincorporated_establishments": PUBLISHED["asuse"]["all_establishments"],
            "own_account_share": PUBLISHED["asuse"]["oae_establishments"] / PUBLISHED["asuse"]["all_establishments"],
            "hired_worker_share": PUBLISHED["asuse"]["hwe_establishments"] / PUBLISHED["asuse"]["all_establishments"],
            "registered_factories": asi_tier["estimated_factories"],
            "productivity_ratio_registered_to_oae": asi_tier["gva_per_person_engaged"] / PUBLISHED["asuse"]["oae_productivity"],
            "productivity_ratio_registered_to_hwe": asi_tier["gva_per_person_engaged"] / PUBLISHED["asuse"]["hwe_productivity"],
        },
        "tiers": {**asuse_tiers, "asi": asi_tier},
        "asuse_sectors": sorted(asuse_sectors, key=lambda row: row["estimated_establishments"], reverse=True),
        "asi_sectors": asi_sectors,
        "plfs": plfs,
        "uncertainty": {
            "asuse_all_activity_gva_per_worker": all_ratio,
            "asuse_all_activity_rse_percent": all_ratio_rse,
            "asuse_manufacturing_gva_per_worker": manufacturing_ratio,
            "asuse_manufacturing_rse_percent": manufacturing_ratio_rse,
            "method": "MoSPI ASUSE 2023-24 Appendix B, section 6 SRSWR ratio approximation",
        },
        "published": PUBLISHED,
        "validation": checks,
        "structure_v1": structure_v1,
        "sources": [
            {
                "id": "asuse",
                "title": "Annual Survey of Unincorporated Sector Enterprises 2023-24",
                "coverage": "Unincorporated non-agricultural establishments; October 2023-September 2024",
                "use": "Enterprise tier, workers, GVA per worker, operating characteristics and NIC sector",
                "url": "https://microdata.gov.in/NADA/index.php/catalog/238",
                "tables": "Published Tables 5, 30, 34 and 36; public-use Blocks 2, 2.1-2.3, 7.1, 8 and 9",
            },
            {
                "id": "asi",
                "title": "Annual Survey of Industries 2023-24",
                "coverage": "Registered factories and other establishments in ASI scope; accounting year 2023-24",
                "use": "Registered factory counts, persons engaged, GVA and workforce structure",
                "url": "https://microdata.gov.in/NADA/index.php/catalog/256",
                "tables": "Public-use Blocks A-J; formulas benchmarked against official ASI tables",
            },
            {
                "id": "plfs",
                "title": "Periodic Labour Force Survey 2023-24",
                "coverage": "People in sampled households; usual-status and current-weekly activity measures; July 2023-June 2024",
                "use": "Worker-side manufacturing share, enterprise size, earnings and regular-worker job quality",
                "url": "https://microdata.gov.in/NADA/index.php/catalog/213",
                "tables": "Published Tables 27, 36, 37, 50 and 51 plus Table 27 RSE; public-use first-visit person file",
            },
        ],
    }

    validate_layer5_contract(output["structure_v1"], checks)
    output = json_safe(output)
    payload = json.dumps(output, indent=2, allow_nan=False) + "\n"
    (PROCESSED / "manufacturing-structure.json").write_text(payload)
    SITE_DATA.write_text(payload)
    (PROCESSED / "validation.json").write_text(json.dumps(checks, indent=2) + "\n")
    try:
        output_label = SITE_DATA.relative_to(ROOT.parent)
    except ValueError:
        output_label = SITE_DATA
    print(f"Wrote {output_label} with {len(checks)} passing validation checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
