# Tamil Nadu Manufacturing: A Structural Snapshot

[Live dashboard](https://smar98.github.io/tamil-nadu-manufacturing-structure/)

A reproducible comparison of enterprise scale, labor productivity and
employment form in Tamil Nadu manufacturing in 2023-24. The project layers
three official MoSPI surveys:

- **ASUSE:** unincorporated manufacturing establishments;
- **ASI:** registered factories and other establishments in ASI scope; and
- **PLFS:** a person-side view of manufacturing employment.

## Research claim

Tamil Nadu has a large owner-operated manufacturing base and a registered
factory sector operating at a much larger average scale. The comparison is a
cross-sectional structural snapshot. It does **not** establish:

- a shortage of medium-sized firms relative to a benchmark;
- the probability that a small establishment becomes a factory;
- that registration or hiring causes higher productivity; or
- which constraint, if any, prevents a particular firm from growing.

The label "missing middle" is therefore treated as an untested hypothesis, not
as the result of this analysis.

## Definitions

- **Unincorporated manufacturer:** a goods-producing establishment not
  incorporated under the Companies Acts or LLP Act. It may still have GST,
  Udyam or other registrations.
- **Own-account establishment (OAE):** no hired worker employed on a fairly
  regular basis. Working owners and unpaid family helpers can still be workers.
- **Hired-worker establishment (HWE):** at least one hired worker employed on a
  fairly regular basis. It is not automatically a registered factory.
- **Registered factory tier:** active manufacturing units in the ASI public-use
  calculation. Its coverage and labor denominator differ from ASUSE.

## Run the site

Requires Node.js `>=22.13.0`.

```bash
npm ci
npm run dev
npm test
```

`npm test` creates the GitHub Pages static export and checks the public data,
methodological warnings, validation gates and absence of obsolete payloads.

## Reproduce the estimates

The website ships with disclosure-safe aggregates, so no restricted unit
records are needed to run it. To recompute the estimates, obtain the ASUSE,
ASI and PLFS public-use files under their applicable MoSPI NADA terms and place
them as documented in [REPRODUCIBILITY.md](research/docs/REPRODUCIBILITY.md).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r research/data/requirements.txt
python3 research/scripts/build_manufacturing_structure.py
npm test
```

The builder stops unless ten predeclared ASUSE and PLFS reconciliation checks
pass. ASI formulas have a separate publication-benchmark audit.

## Repository map

| Path | Purpose |
| --- | --- |
| `app/` | Dashboard interface |
| `public/data/manufacturing-structure.json` | Disclosure-safe web payload |
| `research/scripts/` | ASUSE, ASI and PLFS calculation code |
| `research/derived/` | Auditable aggregate inputs and validation ledgers |
| `research/docs/METHODOLOGY.md` | Estimands, formulas and inferential limits |
| `research/docs/RED_TEAM.md` | Adversarial review of every major claim |
| `research/docs/DATA_DICTIONARY.md` | Field definitions and units |
| `research/docs/REPRODUCIBILITY.md` | Exact end-to-end rebuild instructions |

## Data protection

No FSU, household, person, establishment or factory identifier is committed.
Raw NADA archives are excluded by `.gitignore`; only weighted aggregates and
validation results are public. The code is MIT licensed. Government source
data remain subject to their original terms. Citation metadata are in
`CITATION.cff`.
