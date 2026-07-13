#!/usr/bin/env python3
"""Build the Tamil Nadu manufacturing structure dataset.

The script keeps restricted public-use records local and exports only weighted,
disclosure-safe aggregates. It also fails when unit-level reconstructions drift
materially from MoSPI's published tables.
"""

from __future__ import annotations

import json
import math
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "derived"
SITE_DATA = ROOT.parent / "public" / "data" / "manufacturing-structure.json"
ASUSE_ZIP = RAW / "ASUSE_DATA_2023_24_CSV.zip"
PLFS_ZIP = RAW / "CSV_data_PLFS_2023_2024.zip"
ASI_PANEL = PROCESSED / "asi_aggregates.csv"

TN = "33"
EMPLOYED = {11, 12, 21, 31, 41, 51}

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

PUBLISHED = {
    "asuse": {
        "oae_establishments": 1_118_993,
        "hwe_establishments": 272_663,
        "all_establishments": 1_391_656,
        "oae_productivity": 75_693,
        "hwe_productivity": 187_330,
        "all_productivity": 132_755,
        "all_workers": 2_791_450,
        "source": "ASUSE 2023-24 full report, Tables 5, 30 and 36",
    },
    "plfs": {
        "manufacturing_share": 15.97,
        "male_manufacturing_share": 16.30,
        "female_manufacturing_share": 15.44,
        "rural_manufacturing_share": 12.17,
        "urban_manufacturing_share": 21.73,
        "source": "PLFS 2023-24 annual report, Table 27",
    },
}


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

    base["key"] = unit_key(base, "second_stage_stratum_no")
    reference["key"] = unit_key(reference, "second_stage_stratum_no")
    gva["key"] = unit_key(gva, "second_stage_stratum")
    workers["key"] = unit_key(workers, "second_stage_stratum")

    reference = reference[[
        "key", "ref_period_type", "days_closed_govt_order", "months_in_accounting_period"
    ]]
    gva = gva.loc[gva["item_no"].astype(str).eq("769"), ["key", "value_rs"]]
    workers = workers.loc[workers["item_no"].astype(str).eq("789"), [
        "key", "full_time_male", "full_time_female", "full_time_trans",
        "part_time_male", "part_time_female", "part_time_trans", "total_workers",
    ]]

    frame = base.merge(reference, on="key", validate="one_to_one")
    frame = frame.merge(gva, on="key", validate="one_to_one")
    frame = frame.merge(workers, on="key", validate="one_to_one")
    frame = frame.loc[frame["nss_region"].astype(str).str.startswith(TN)].copy()

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
    frame["annual_gva"] = frame["value_rs"] * frame["annual_factor"]
    worker_columns = [
        "full_time_male", "full_time_female", "full_time_trans",
        "part_time_male", "part_time_female", "part_time_trans",
    ]
    frame[worker_columns] = frame[worker_columns].fillna(0)
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
        record = {
            "nic2": int(nic),
            "label": NIC2.get(int(nic), f"NIC {int(nic):02d}"),
            "sample_establishments": int(len(group)),
            "estimated_establishments": round(float(establishments)),
            "hwe_share": weighted_share(group, group["est_type"].eq(1)),
            "workers_per_establishment": weighted_ratio(group, "total_workers", "establishment_unit"),
            "gva_per_worker": weighted_ratio(group, "annual_gva", "total_workers"),
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
        tiers[key] = {
            "label": label,
            "sample_establishments": int(len(group)),
            "estimated_establishments": round(float(group["weight"].sum())),
            "estimated_workers": round(float((group["total_workers"] * group["weight"]).sum())),
            "workers_per_establishment": weighted_ratio(group, "total_workers", "establishment_unit"),
            "gva_per_worker": weighted_ratio(group, "annual_gva", "total_workers"),
            "female_worker_share": weighted_ratio(group, "female_workers", "all_gender_workers"),
        }
    return sectors, tiers


def plfs_summary() -> dict:
    with zipfile.ZipFile(PLFS_ZIP) as archive:
        member = next(name for name in archive.namelist() if name.endswith("/perv1.csv"))
        columns = [
            "state_perv1", "b1q3_perv1", "b4q5_perv1", "b5pt1q3_perv1",
            "b5pt1q5_perv1", "b5pt2q3_perv1", "b5pt2q5_perv1", "mult_perv1",
        ]
        frame = pd.read_csv(archive.open(member), usecols=columns, low_memory=False)

    frame = frame.loc[frame["state_perv1"].eq(33)].copy()
    principal = frame["b5pt1q3_perv1"].isin(EMPLOYED)
    subsidiary = frame["b5pt2q3_perv1"].isin(EMPLOYED)
    frame = frame.loc[principal | subsidiary].copy()
    frame["status"] = np.where(principal.loc[frame.index], frame["b5pt1q3_perv1"], frame["b5pt2q3_perv1"])
    frame["nic"] = np.where(principal.loc[frame.index], frame["b5pt1q5_perv1"], frame["b5pt2q5_perv1"])
    frame["manufacturing"] = frame["nic"].between(10_000, 33_999)
    frame["weight"] = frame["mult_perv1"].astype(float)

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
        "male_manufacturing_share": share(frame.loc[frame["b4q5_perv1"].eq(1)]),
        "female_manufacturing_share": share(frame.loc[frame["b4q5_perv1"].eq(2)]),
        "rural_manufacturing_share": share(frame.loc[frame["b1q3_perv1"].eq(1)]),
        "urban_manufacturing_share": share(frame.loc[frame["b1q3_perv1"].eq(2)]),
        "manufacturing_status_shares": status_shares,
    }


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


def assert_close(name: str, actual: float, expected: float, relative_tolerance: float) -> dict:
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

    asuse_all = asuse_frame()
    asuse = asuse_all.loc[asuse_all["major_nic_2dig"].between(10, 33)].copy()
    asuse["establishment_unit"] = 1.0
    asuse_sectors, asuse_tiers = summarize_asuse(asuse)
    for tier_key in ("oae", "hwe"):
        asuse_tiers[tier_key]["reconstructed_gva_per_worker"] = asuse_tiers[tier_key]["gva_per_worker"]
        asuse_tiers[tier_key]["gva_per_worker"] = PUBLISHED["asuse"][f"{tier_key}_productivity"]
    plfs = plfs_summary()
    asi_tier, asi_sectors = asi_summary()
    all_ratio, all_ratio_rse = ratio_rse(
        asuse_all,
        asuse_all["major_nic_5dig"].ne(68_108),
    )
    manufacturing_ratio, manufacturing_ratio_rse = ratio_rse(
        asuse_all,
        asuse_all["major_nic_2dig"].between(10, 33),
    )

    checks = []
    for key, published_key in [("oae", "oae_establishments"), ("hwe", "hwe_establishments")]:
        checks.append(assert_close(
            f"ASUSE TN manufacturing {key.upper()} establishments",
            asuse_tiers[key]["estimated_establishments"],
            PUBLISHED["asuse"][published_key],
            0.001,
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

    output = {
        "meta": {
            "title": "Tamil Nadu Manufacturing: A Structural Snapshot",
            "built_from": ["ASUSE 2023-24", "ASI 2023-24", "PLFS 2023-24"],
            "price_basis": "Current rupees; no time-series growth claim is made.",
            "comparison_warning": (
                "The three surveys cover different statistical units and overlapping but non-identical "
                "reference periods. Comparisons diagnose structure; they do not track firm transitions."
            ),
            "disclosure": "Only weighted aggregates are exported. No respondent-level record is published.",
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
        "sources": [
            {
                "id": "asuse",
                "title": "Annual Survey of Unincorporated Sector Enterprises 2023-24",
                "coverage": "Unincorporated non-agricultural establishments; October 2023-September 2024",
                "use": "Enterprise tier, workers, GVA per worker, operating characteristics and NIC sector",
                "url": "https://microdata.gov.in/NADA/index.php/catalog/238",
                "tables": "Published Tables 5, 30 and 36; public-use Blocks 2, 2.1-2.3, 7.1 and 8",
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
                "coverage": "Usually working persons (principal plus subsidiary status); July 2023-June 2024",
                "use": "Independent worker-side manufacturing share and employment status",
                "url": "https://microdata.gov.in/NADA/index.php/catalog/213",
                "tables": "Published Table 27; public-use first-visit person file",
            },
        ],
    }

    output = json_safe(output)
    payload = json.dumps(output, indent=2, allow_nan=False) + "\n"
    (PROCESSED / "manufacturing-structure.json").write_text(payload)
    SITE_DATA.write_text(payload)
    (PROCESSED / "validation.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(f"Wrote {SITE_DATA.relative_to(ROOT.parent)} with {len(checks)} passing validation checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
