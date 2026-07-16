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

- the probability that a small establishment becomes a factory;
- that registration or hiring causes higher productivity; or
- which constraint, if any, prevents a particular firm from growing.

Within registered ASI units, the project tests four middle definitions (`10–249`,
`10–99`, `20–249` and `50–249`) under equal-allocation and whole-return sizing
treatments. Tamil Nadu does not show an unusually small middle within those bounded
tests. This is not a continuous ASUSE-to-ASI firm-growth ladder.

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

The builder stops before writing unless all 28 predeclared reconciliation checks
pass and the fail-closed Layer 5 contract validates row coverage, permitted
adjustments, source preservation, support, decompositions, suppression and
identifier exclusion. ASI formulas also have a separate publication-benchmark audit.

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
Raw NADA archives are excluded by `.gitignore`. Public artifacts contain weighted
aggregates, labels, unweighted sample counts, validation results and disclosure
flags, but no respondent-level records or linkage identifiers. The code is MIT
licensed. Government source data remain subject to their original terms. Citation
metadata are in `CITATION.cff`.
