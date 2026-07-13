"""NIC2-level Kitagawa sensitivity with true employment weights from raw ASI.
Read-only scratch analysis; output is aggregate-only (no cell values printed for
payload-suppressed cells). Cells restricted to jointly published payload cells."""
import sys, json, collections
sys.path.insert(0, "/Users/sanch/Desktop/tamil-nadu-manufacturing-structure/research/scripts")
import build_manufacturing_structure as B

frame = B.asi_structure_frame()
GEO = {"33": "TN", "24": "GJ", "27": "MH", "29": "KA", "36": "TG", "32": "KL"}
PEERS = ["IN", "24", "27", "29", "36", "32"]

p = json.load(open("/Users/sanch/Desktop/tamil-nadu-manufacturing-structure/public/data/manufacturing-structure.json"))
sv = p["structure_v1"]
pub_rate = {}  # (geo, nic2) -> published rate (None if suppressed)
for r in sv["value_addition"]:
    if r["survey"] == "asi" and r["dimension"] == "industry":
        pub_rate[(r["geography_id"], r["nic2"])] = r["per_person_value"]
pub7 = {r["comparator_id"]: r for r in sv["peer_comparisons_adjusted"]
        if r["survey"] == "asi" and r["outcome"] == "gva_per_person_engaged"
        and r["adjustment_dimension"] == "industry"}
pub7x4 = {r["comparator_id"]: r for r in sv["peer_comparisons_adjusted"]
          if r["survey"] == "asi" and r["outcome"] == "gva_per_person_engaged"
          and r["adjustment_dimension"] == "industry_size"}

def geo_cells(code):
    """nic2 -> (employment, gva) using weighted contributions, one geography."""
    g = frame if code == "IN" else frame.loc[frame["state"].eq(code)]
    out = {}
    for nic2, grp in g.groupby("nic2"):
        E = float((grp["weight"] * grp["employees"]).sum())
        Y = float((grp["weight"] * grp["gva"]).sum())
        if E > 0:
            out[int(nic2)] = (E, Y)
    return out

cells_by_geo = {c: geo_cells(c) for c in ["33"] + PEERS}

# cross-check: raw rates vs payload published rates (validates the scratch frame)
maxdev = 0.0
for (geo, nic2), rate in pub_rate.items():
    if rate is None: continue
    E, Y = cells_by_geo[geo][nic2]
    maxdev = max(maxdev, abs(Y / E - rate) / rate)
print(f"cross-check: max relative deviation raw-vs-payload NIC2 rates = {maxdev:.2e}\n")

print("=== NIC2-level (24-industry) symmetric Kitagawa, ASI GVA/person, true employment weights ===")
for c in PEERS:
    tn, cmp_ = cells_by_geo["33"], cells_by_geo[c]
    lbl = "IN" if c == "IN" else GEO[c]
    cells = sorted(i for i in set(tn) & set(cmp_)
                   if pub_rate.get(("33", i)) is not None and pub_rate.get((c, i)) is not None)
    Et, Ec = sum(tn[i][0] for i in cells), sum(cmp_[i][0] for i in cells)
    cov_t = Et / sum(v[0] for v in tn.values())
    cov_c = Ec / sum(v[0] for v in cmp_.values())
    wt = {i: tn[i][0] / Et for i in cells}
    wc = {i: cmp_[i][0] / Ec for i in cells}
    rt = {i: tn[i][1] / tn[i][0] for i in cells}
    rc = {i: cmp_[i][1] / cmp_[i][0] for i in cells}
    gap = sum(wt[i] * rt[i] for i in cells) - sum(wc[i] * rc[i] for i in cells)
    comp = sum((wt[i] - wc[i]) * (rt[i] + rc[i]) / 2 for i in cells)
    within = sum((wt[i] + wc[i]) / 2 * (rt[i] - rc[i]) for i in cells)
    print(f"TN vs {lbl}: cells={len(cells)}/24  emp coverage TN {cov_t:.1%} / cmp {cov_c:.1%}")
    print(f"  NIC2-24 : gap {gap:>12,.0f}  mix {comp/gap:6.1%}  within {within/gap:6.1%}")
    for tag, row in (("pub 7grp", pub7.get(c)), ("pub 7x4 ", pub7x4.get(c))):
        if row and row.get("common_support_raw_gap") is not None:
            g0 = row["common_support_raw_gap"]
            print(f"  {tag}: gap {g0:>12,.0f}  mix {row['composition_component']/g0:6.1%}  within {row['within_component']/g0:6.1%}")
        elif row:
            print(f"  {tag}: SUPPRESSED in published table (reason: {row.get('suppression_reason')})")
    # how many retained NIC2 cells have TN's rate below the comparator's, employment-weighted
    below = [i for i in cells if rt[i] < rc[i]]
    share_emp_below = sum((wt[i] + wc[i]) / 2 for i in below)
    print(f"  TN rate below {lbl} in {len(below)}/{len(cells)} cells, covering {share_emp_below:.0%} of common-weight employment\n")

# ---------------------------------------------------------------------------
# Parts (b) and (c): multi-year persistence and capital intensity, from the
# committed ASI panel (research/derived/asi_aggregates.csv). Descriptive only.
# ---------------------------------------------------------------------------
import csv

rows = list(csv.DictReader(open(
    "/Users/sanch/Desktop/tamil-nadu-manufacturing-structure/research/derived/asi_aggregates.csv")))

def _f(r, k):
    v = r[k]
    return float(v) if v not in ("", None) else None

panel, cap = {}, {}
for r in rows:
    g, e, fc = _f(r, "gva"), _f(r, "employees"), _f(r, "fixed_capital")
    if g and e:
        panel[(r["year"], r["state"], r["sector_id"])] = g / e
    if fc and e:
        cap[(r["year"], r["state"], r["sector_id"])] = fc / e

assert round(panel[("2023", "33", "all-manufacturing")]) == 839770  # payload calibration

print("\n=== (b) all-manufacturing GVA/employee, sign of TN-peer gap, 2008..2023 ===")
years = [str(y) for y in range(2008, 2024)]
for c in ["24", "27", "29", "36", "32"]:
    s = "".join(
        "-" if (panel.get((y, "33", "all-manufacturing")) or 0)
        < (panel.get((y, c, "all-manufacturing")) or 9e9) else "+"
        for y in years)
    t, k = panel[("2023", "33", "all-manufacturing")], panel[("2023", c, "all-manufacturing")]
    print(f"TN vs {GEO[c]}: {s}  2023 ratio {t / k:.2f}")

print("\n=== (b2) named sectors 2020-2023 and (c) capital intensity 2023: TN/peer ratios ===")
sectors = sorted(set(s for (_, _, s) in panel) - {"all-manufacturing"})
hdr = f"{'sector':<24}" + "".join(f"{GEO[c]:>7}" for c in ["24", "27", "29", "36", "32"])
for label, table in (("GVA/employee 2023", panel), ("fixed capital/employee 2023", cap)):
    print(f"\n{label}:")
    print(hdr)
    for s in ["all-manufacturing"] + sectors:
        t = table.get(("2023", "33", s))
        if not t:
            continue
        line = f"{s:<24}"
        for c in ["24", "27", "29", "36", "32"]:
            k = table.get(("2023", c, s))
            line += f"{t / k:>7.2f}" if k else f"{'·':>7}"
        print(line)
