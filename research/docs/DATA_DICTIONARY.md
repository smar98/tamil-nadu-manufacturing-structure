# Data Dictionary

The public payload is `public/data/manufacturing-structure.json`. All counts
and ratios are survey-weighted unless explicitly labeled as sample counts.

## Headline and tiers

| Field | Definition | Unit |
| --- | --- | --- |
| `unincorporated_establishments` | Estimated Tamil Nadu manufacturing establishments in ASUSE scope | count |
| `own_account_share` | OAE establishments divided by all ASUSE manufacturing establishments | proportion, 0-1 |
| `hired_worker_share` | HWE establishments divided by all ASUSE manufacturing establishments | proportion, 0-1 |
| `registered_factories` | Estimated active manufacturing factories in the ASI calculation | count |
| `workers_per_establishment` | Weighted workers divided by weighted establishments | people per establishment |
| `persons_per_factory` | Weighted persons engaged divided by weighted factories | people per factory |
| `gva_per_worker` | Annual current-price GVA divided by workers | rupees per year |
| `gva_per_person_engaged` | Annual current-price GVA divided by persons engaged | rupees per year |

## ASUSE sectors

| Field | Definition |
| --- | --- |
| `nic2` | NIC 2008 two-digit manufacturing division |
| `sample_establishments` | Unweighted records contributing to the domain |
| `estimated_establishments` | Survey-weighted establishment count |
| `hwe_share` | Share classified as hired-worker establishments |
| `computer_use_share` | Share reporting computer use during the reference period |
| `internet_use_share` | Share reporting internet use |
| `accounts_share` | Share reporting maintained accounts |
| `bank_account_share` | Share reporting a business or personal bank account used by the establishment |

These characteristics are correlates. They are not estimated causes of hiring
or productivity.

## ASI sectors

Sector definitions are explicit NIC-prefix groups in
`research/data/asi_sector_definitions.json`. `rd_factory_share` and
`training_factory_share` are weighted shares of factories reporting the
respective item. They do not measure research quality, innovation output or
worker skill.

## PLFS

`manufacturing_share` is the share of usually working people whose principal
or, where applicable, subsidiary activity is manufacturing. Employment-status
shares partition manufacturing workers into self-employed, regular wage and
casual labor. They are not a crosswalk to OAE, HWE or ASI establishments.

## Validation

Each validation record stores the reconstructed value, official published
value, relative error and pass/fail status. The build writes no payload unless
all gates pass.
