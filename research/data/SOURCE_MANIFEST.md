# Source Acquisition Manifest

Raw unit-record archives are not redistributed. Obtain them lawfully from the
linked MoSPI NADA catalogs and verify them against `RAW_SHA256SUMS`.

| File | Official source | Used for |
| --- | --- | --- |
| `ASUSE_DATA_2023_24_CSV.zip` | [ASUSE catalog 238](https://microdata.gov.in/NADA/index.php/catalog/238) | OAE/HWE structure, workers and GVA |
| `CSV_data_PLFS_2023_2024.zip` | [PLFS catalog 213](https://microdata.gov.in/NADA/index.php/catalog/213) | Worker-side manufacturing composition |
| `ASI_DATA_YYYY_YY_CSV.zip` | [ASI catalog](https://microdata.gov.in/NADA/index.php/catalog/ASI) | Registered factory aggregates |

Published reference tables and concepts:

- ASUSE 2023-24 full report, Tables 5, 30 and 36 and Appendix B.
- PLFS 2023-24 annual report, Table 27.
- ASI 2023-24 instruction manual, Annexure VIII.
- ASI official Tamil Nadu totals listed in `official_asi_benchmarks.csv`.

The checksums identify the exact ASUSE and PLFS files used for the published
payload. ASI benchmark source URLs are recorded row by row in the benchmark
CSV and validation ledger.
