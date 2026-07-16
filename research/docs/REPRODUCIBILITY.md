# Reproducibility

## Reproduction levels

### Website-only reproduction

No survey microdata are required:

```bash
npm ci
npm test
```

This rebuilds the static site from the committed aggregate JSON.

### Canonical 2023-24 payload

This step requires locally authorized copies of:

```text
research/data/raw/ASUSE_DATA_2023_24_CSV.zip
research/data/raw/CSV_data_PLFS_2023_2024.zip
research/data/raw/asi/ASI_DATA_2023_24_CSV.zip
research/derived/asi_aggregates.csv
```

The ASI CSV supplies the legacy interface summary. The 2023-24 ASI archive supplies the return-level inputs needed for establishment size, GVA, emoluments and the labour-cost proxy. The PLFS first-visit person file supplies usual-status job quality and current-weekly earnings; identifiers are used only for private design diagnostics. Neither respondent records nor linkage identifiers are exported.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r research/data/requirements.txt
python3 research/scripts/build_manufacturing_structure.py
npm test
```

The builder writes:

```text
public/data/manufacturing-structure.json
research/derived/manufacturing-structure.json
research/derived/validation.json
```

The two manufacturing-structure JSON files must be byte-identical. Before any payload or validation-ledger write, the builder requires exactly 28 passing predeclared reconciliation gates and validates the complete Layer 5 contract: 78 raw rows, 78 adjusted rows, declared coverage, source and PLFS-interval preservation, permitted adjustment dimensions, support thresholds, decomposition identities, suppression nulling and identifier exclusion.

The canonical payload contains Layers 1–5, including 78 raw and 78 composition-adjusted peer-comparison rows (72 stable, 6 mechanically suppressed Kerala ASI adjustments). The Layer 5 payload-contract test runs against the canonical payload and must pass rather than skip.

### Layer 6 exploratory appendix

A separate standalone script builds the disclosure-safe ASUSE reported-problems appendix
(exploratory correlations, not part of the canonical payload):

```bash
python3 research/scripts/build_asuse_problems_appendix.py
```

It reads only `research/data/raw/ASUSE_DATA_2023_24_CSV.zip` and writes
`research/derived/asuse_problems_appendix.json`. Its self-check reconciles weighted
establishment totals against the published Layer 1 gates and enforces the Layer 3
disclosure rule on every published cell. The run is deterministic. Documentation:
`research/docs/LAYER6_ASUSE_PROBLEMS_APPENDIX.md`.

Expected gates include:

- 1,118,993 Tamil Nadu manufacturing OAEs;
- 272,663 Tamil Nadu manufacturing HWEs;
- 1,078,944 Tamil Nadu manufacturing hired workers;
- ₹140,133 annual emoluments per hired worker;
- a 15.97% PLFS manufacturing worker share;
- PLFS Tables 36 and 37 employment-condition and enterprise-size benchmarks;
- ₹443 across 8,771 manufacturing casual-labour person-days in PLFS Table 51;
- a 12.17% Tamil Nadu rural manufacturing share with 5.81% paired-subsample RSE.

### Full ASI reconstruction

Obtain the required ASI CSV archives from MoSPI NADA and place them in `research/data/raw/asi/` using names such as:

```text
ASI_DATA_2014_15_CSV.zip
ASI_DATA_2015_16_CSV.zip
ASI_DATA_2023_24_CSV.zip
```

To recreate the complete panel, supply all archives from 2008-09 through 2023-24 and run:

```bash
python3 research/scripts/build_asi_aggregates.py --start-year 2008 --end-year 2023
python3 research/scripts/validate_asi_aggregates.py
python3 research/scripts/build_manufacturing_structure.py
npm test
```

Validation requires at least the 2014-15, 2015-16 and 2023-24 archives because those years have committed official benchmark totals.

`build_asi_aggregates.py` keeps suppress-grade cells in memory for classification, then writes only non-suppress rows to `research/derived/asi_aggregates.csv` and the ASI JSON. The CSV is an aggregate analytical input, not respondent-level data. Cells with fewer than 10 sampled returns or excessive GVA concentration are omitted.

## Data flow

```text
ASUSE unit records --------------------\
PLFS person records --------------------+--> build_manufacturing_structure.py --> canonical public JSON
ASI 2023-24 return records -------------/                 ^
                                                           |
ASI historical return records --> build_asi_aggregates.py -+--> disclosure-filtered aggregate CSV
                                  |
                                  +--> validate_asi_aggregates.py --> benchmark ledger
```

Raw survey archives remain local. Public outputs contain weighted aggregates, labels, unweighted sample counts, validation results and disclosure flags, but no respondent-level records or linkage identifiers.

## Integrity and expected outputs

- Raw archive checksums: `research/data/RAW_SHA256SUMS`
- Published benchmark inputs: `research/data/official_asi_benchmarks.csv`
- Canonical validation ledger: `research/derived/validation.json`
- ASI benchmark ledger: `research/derived/asi_benchmark_validation.json`
- Canonical web payload: `public/data/manufacturing-structure.json`

The repository never requires an API key, cookie or authorization header at runtime. Data acquisition is deliberately outside the code because NADA access must occur through an authorized account.

## Environment

The canonical payload was rebuilt with the publication environment:

- CPython `3.9.6`
- NumPy `2.0.2`
- pandas `2.3.3`
- Node.js `>=22.13.0`

`package-lock.json` pins the JavaScript dependency graph, and `research/data/requirements.txt` pins the Python packages used for publication.
