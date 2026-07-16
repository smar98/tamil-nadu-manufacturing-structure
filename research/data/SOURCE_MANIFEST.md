# Source Acquisition Manifest

Raw unit-record archives are not redistributed. Obtain them lawfully from the
linked MoSPI NADA catalogs and verify them against `RAW_SHA256SUMS`.

| File | Official source | Used for |
| --- | --- | --- |
| `ASUSE_DATA_2023_24_CSV.zip` | [ASUSE catalog 238](https://microdata.gov.in/NADA/index.php/catalog/238) | OAE/HWE structure, workers and GVA |
| `CSV_data_PLFS_2023_2024.zip` | [PLFS catalog 213](https://microdata.gov.in/NADA/index.php/catalog/213) | Worker-side manufacturing composition |
| `ASI_DATA_2023_24_CSV.zip` | [ASI 2023-24 catalog 256](https://microdata.gov.in/NADA/index.php/catalog/256), reference ID `DDI-IND-NSO-ASI-2023-24` | Canonical registered-factory structure and outcomes |
| `ASI_DATA_YYYY_YY_CSV.zip` | Year-specific [ASI catalogs](https://microdata.gov.in/NADA/index.php/catalog/ASI) | Optional historical registered-factory panel |

Published reference tables and concepts:

- ASUSE 2023-24 full report, Tables 5, 30 and 36 and Appendix B.
- PLFS 2023-24 annual report, Table 27.
- ASI 2023-24 instruction manual, Annexure VIII.
- ASI official Tamil Nadu totals listed in `official_asi_benchmarks.csv`.

The checksums identify the exact ASUSE, PLFS and canonical 2023-24 ASI archives
used for the published payload. Historical ASI benchmark source URLs are recorded
row by row in the benchmark CSV and validation ledger.
