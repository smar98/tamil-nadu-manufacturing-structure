"""Aggregate-only NIC2 sensitivity and panel robustness checks for ASI."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_manufacturing_structure as B

RAW_PAYLOAD_TOLERANCE = 1e-12
GEO = {"33": "TN", "24": "GJ", "27": "MH", "29": "KA", "36": "TG", "32": "KL"}
PEERS = ["IN", "24", "27", "29", "36", "32"]

frame = B.asi_structure_frame()
with (ROOT.parent / "public" / "data" / "manufacturing-structure.json").open() as handle:
    payload = json.load(handle)
structure = payload["structure_v1"]

pub_rate = {
    (row["geography_id"], row["nic2"]): row["per_person_value"]
    for row in structure["value_addition"]
    if row["survey"] == "asi" and row["dimension"] == "industry"
}
pub7 = {
    row["comparator_id"]: row
    for row in structure["peer_comparisons_adjusted"]
    if row["survey"] == "asi"
    and row["outcome"] == "gva_per_person_engaged"
    and row["adjustment_dimension"] == "industry"
}
pub7x4 = {
    row["comparator_id"]: row
    for row in structure["peer_comparisons_adjusted"]
    if row["survey"] == "asi"
    and row["outcome"] == "gva_per_person_engaged"
    and row["adjustment_dimension"] == "industry_size"
}


def geo_cells(code):
    """Return NIC2 -> (employment, GVA) from weighted contributions."""
    geography = frame if code == "IN" else frame.loc[frame["state"].eq(code)]
    cells = {}
    for nic2, group in geography.groupby("nic2"):
        employment = float((group["weight"] * group["employees"]).sum())
        gva = float((group["weight"] * group["gva"]).sum())
        if employment > 0:
            cells[int(nic2)] = (employment, gva)
    return cells


cells_by_geo = {code: geo_cells(code) for code in ["33", *PEERS]}

deviations = []
for (geography, nic2), rate in pub_rate.items():
    if rate is None:
        continue
    employment, gva = cells_by_geo[geography][nic2]
    scale = max(abs(rate), 1.0)
    deviations.append(abs(gva / employment - rate) / scale)
if not deviations:
    raise AssertionError("No raw/payload NIC2 rates were available for reconciliation")
max_deviation = max(deviations)
if max_deviation > RAW_PAYLOAD_TOLERANCE:
    raise AssertionError(
        f"Raw/payload NIC2 rate deviation {max_deviation:.2e} exceeds "
        f"{RAW_PAYLOAD_TOLERANCE:.0e}"
    )
print(f"cross-check: max relative deviation raw-vs-payload NIC2 rates = {max_deviation:.2e}\n")

print("=== NIC2-level (24-industry) symmetric Kitagawa, ASI GVA/person, true employment weights ===")
for code in PEERS:
    tn, comparator = cells_by_geo["33"], cells_by_geo[code]
    label = "IN" if code == "IN" else GEO[code]
    cells = sorted(
        nic2
        for nic2 in set(tn) & set(comparator)
        if pub_rate.get(("33", nic2)) is not None and pub_rate.get((code, nic2)) is not None
    )
    tn_employment = sum(tn[nic2][0] for nic2 in cells)
    comparator_employment = sum(comparator[nic2][0] for nic2 in cells)
    tn_coverage = tn_employment / sum(value[0] for value in tn.values())
    comparator_coverage = comparator_employment / sum(value[0] for value in comparator.values())
    tn_weight = {nic2: tn[nic2][0] / tn_employment for nic2 in cells}
    comparator_weight = {
        nic2: comparator[nic2][0] / comparator_employment for nic2 in cells
    }
    tn_rate = {nic2: tn[nic2][1] / tn[nic2][0] for nic2 in cells}
    comparator_rate = {
        nic2: comparator[nic2][1] / comparator[nic2][0] for nic2 in cells
    }
    gap = sum(tn_weight[nic2] * tn_rate[nic2] for nic2 in cells) - sum(
        comparator_weight[nic2] * comparator_rate[nic2] for nic2 in cells
    )
    composition = sum(
        (tn_weight[nic2] - comparator_weight[nic2])
        * (tn_rate[nic2] + comparator_rate[nic2])
        / 2
        for nic2 in cells
    )
    within = sum(
        (tn_weight[nic2] + comparator_weight[nic2])
        / 2
        * (tn_rate[nic2] - comparator_rate[nic2])
        for nic2 in cells
    )
    print(
        f"TN vs {label}: cells={len(cells)}/24  emp coverage TN {tn_coverage:.1%} "
        f"/ cmp {comparator_coverage:.1%}"
    )
    print(f"  NIC2-24 : gap {gap:>12,.0f}  mix {composition/gap:6.1%}  within {within/gap:6.1%}")
    for tag, row in (("pub 7grp", pub7.get(code)), ("pub 7x4 ", pub7x4.get(code))):
        if row and row.get("common_support_raw_gap") is not None:
            published_gap = row["common_support_raw_gap"]
            print(
                f"  {tag}: gap {published_gap:>12,.0f}  "
                f"mix {row['composition_component']/published_gap:6.1%}  "
                f"within {row['within_component']/published_gap:6.1%}"
            )
        elif row:
            print(
                f"  {tag}: SUPPRESSED in published table "
                f"(reason: {row.get('suppression_reason')})"
            )
    below = [nic2 for nic2 in cells if tn_rate[nic2] < comparator_rate[nic2]]
    share_employment_below = sum(
        (tn_weight[nic2] + comparator_weight[nic2]) / 2 for nic2 in below
    )
    print(
        f"  TN rate below {label} in {len(below)}/{len(cells)} cells, "
        f"covering {share_employment_below:.0%} of common-weight employment\n"
    )


def number(row, key):
    value = row[key]
    return float(value) if value not in ("", None) else None


with (ROOT / "derived" / "asi_aggregates.csv").open(newline="") as handle:
    rows = list(csv.DictReader(handle))

panel, capital = {}, {}
for row in rows:
    gva = number(row, "gva")
    employment = number(row, "employees")
    fixed_capital = number(row, "fixed_capital")
    if gva is not None and employment is not None and employment > 0:
        panel[(row["year"], row["state"], row["sector_id"])] = gva / employment
    if fixed_capital is not None and employment is not None and employment > 0:
        capital[(row["year"], row["state"], row["sector_id"])] = fixed_capital / employment

assert round(panel[("2023", "33", "all-manufacturing")]) == 839770


def gap_marker(year, comparator):
    tn = panel.get((year, "33", "all-manufacturing"))
    peer = panel.get((year, comparator, "all-manufacturing"))
    if tn is None or peer is None:
        return "·"
    return "-" if tn < peer else "+"


print("\n=== (b) all-manufacturing GVA/person engaged, sign of TN-peer gap, 2008..2023 ===")
years = [str(year) for year in range(2008, 2024)]
for code in ["24", "27", "29", "36", "32"]:
    markers = [gap_marker(year, code) for year in years]
    signs = "".join(markers)
    tn_2023 = panel.get(("2023", "33", "all-manufacturing"))
    peer_2023 = panel.get(("2023", code, "all-manufacturing"))
    ratio = f"{tn_2023 / peer_2023:.2f}" if tn_2023 is not None and peer_2023 is not None else "·"
    completeness = "complete" if "·" not in markers else "incomplete; no all-years conclusion"
    print(f"TN vs {GEO[code]}: {signs}  2023 ratio {ratio}  [{completeness}]")

print("\n=== (b2) named sectors 2020-2023 and (c) capital intensity 2023: TN/peer ratios ===")
sectors = sorted(set(sector for _, _, sector in panel) - {"all-manufacturing"})
header = f"{'sector':<24}" + "".join(f"{GEO[code]:>7}" for code in ["24", "27", "29", "36", "32"])
for label, table in (("GVA/person engaged 2023", panel), ("fixed capital/person engaged 2023", capital)):
    print(f"\n{label}:")
    print(header)
    for sector in ["all-manufacturing", *sectors]:
        tn = table.get(("2023", "33", sector))
        if tn is None:
            continue
        line = f"{sector:<24}"
        for code in ["24", "27", "29", "36", "32"]:
            peer = table.get(("2023", code, sector))
            line += f"{tn / peer:>7.2f}" if peer is not None and peer != 0 else f"{'·':>7}"
        print(line)
