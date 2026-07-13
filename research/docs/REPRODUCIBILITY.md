# Reproducibility

## Reproduction levels

### Website-only reproduction

No restricted data are required:

```bash
npm ci
npm test
```

This rebuilds the static site from the committed aggregate JSON.

### Final-estimate reproduction

Requires ASUSE and PLFS public-use archives obtained under the applicable NADA
terms. Place exactly these files in `research/data/raw/`:

```text
ASUSE_DATA_2023_24_CSV.zip
CSV_data_PLFS_2023_2024.zip
```

The committed `research/derived/asi_aggregates.csv` is a disclosure-safe input
to this step.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r research/data/requirements.txt
python3 research/scripts/build_manufacturing_structure.py
npm test
```

Expected headline gates include 1,391,656 Tamil Nadu unincorporated
manufacturing establishments, 1,118,993 OAEs and a PLFS manufacturing worker
share of 15.97%.

### Full ASI reconstruction

Obtain the required ASI CSV archives from MoSPI NADA and place them in
`research/data/raw/asi/` using names such as:

```text
ASI_DATA_2014_15_CSV.zip
ASI_DATA_2015_16_CSV.zip
ASI_DATA_2023_24_CSV.zip
```

To recreate the complete committed panel, supply all archives from 2008-09
through 2023-24 and run:

```bash
python3 research/scripts/build_asi_aggregates.py --start-year 2008 --end-year 2023
python3 research/scripts/validate_asi_aggregates.py
python3 research/scripts/build_manufacturing_structure.py
npm test
```

Validation requires at least the 2014-15, 2015-16 and 2023-24 archives because
those years have committed official benchmark totals.

## Data flow

```text
ASUSE unit records ----\
                        +--> build_manufacturing_structure.py --> public JSON
PLFS unit records -----/                  ^
                                           |
ASI unit records --> build_asi_aggregates.py --> disclosure-safe ASI CSV
                         |
                         +--> validate_asi_aggregates.py --> benchmark ledger
```

## Integrity and expected outputs

- Raw archive checksums: `research/data/RAW_SHA256SUMS`
- Published benchmark inputs: `research/data/official_asi_benchmarks.csv`
- Final validation cells: `research/derived/validation.json`
- ASI benchmark ledger: `research/derived/asi_benchmark_validation.json`
- Web payload: `public/data/manufacturing-structure.json`

The repository never requires an API key, cookie or authorization header at
runtime. Data acquisition is deliberately outside the code because NADA access
must occur through the user's authorized account.

## Environment

- Python 3.11 or newer
- NumPy `>=1.26,<3`
- pandas `>=2.2,<3`
- Node.js `>=22.13.0`

`package-lock.json` pins the JavaScript dependency graph. Python package ranges
are intentionally narrow; record exact installed versions with `pip freeze`
when producing an archival replication.
