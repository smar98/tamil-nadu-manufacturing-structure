# Existing-analysis verification

Overlap verdict for the project against already-published analyses, per the handoff's
existing-analysis verification requirement. Each source was checked with a bounded,
source-specific verification (2026-07-13); academic sources rely on the prior workflow's
adversarially verified claims and were not re-run. Classification scale: **exact
duplication** / **partial overlap** / **contextual background** / (feeds the) **genuine
contribution**.

## Verdict in one paragraph

No source publishes the project's central results. But the overlap is materially larger than
the project previously assumed, and in one case — the Tamil Nadu Economic Survey 2025–26 —
an official document already publishes a TN manufacturing size-class distribution for the
same 2023–24 year and already invokes the missing-middle literature. Novelty claims must be
tempered and specific: the project's genuine contribution is (1) the survey-separated,
full-size-range, peer-state diagnostic with disclosure and uncertainty discipline; (2)
per-person outcome ratios at state × industry cells that MoSPI never computes; (3) the
Kitagawa-style composition-adjusted peer comparisons, published nowhere; (4)
manufacturing-specific state worker earnings and job quality with design-based intervals,
which the PLFS report does not publish; and (5) the verified finding-to-instrument policy
map. The project must cite the overlapping official tables wherever its exhibits sit near
them.

## Source classifications

### ASUSE 2023–24 official report (MoSPI) — partial overlap

Already published at state level, by broad activity including manufacturing: establishment
counts (Table 5), workers (Tables 29–32), **GVA per worker (Table 36)**, GVA per
establishment (Table 38), **emoluments per hired worker (Table 34)**. The project's Layer 3
ASUSE overall state values therefore duplicate official statistics (they are reconciliation
gates, not discoveries). Not published: state-level size-band distributions (Table 42 is
all-India only), state × NIC2 outcome detail, industry-standardized comparisons, any
missing-middle analysis. **The state-level ASUSE manufacturing size distribution is
unpublished anywhere; it is a genuine contribution.**

### PLFS 2023–24 annual report (MoSPI) — partial overlap

Already published at state level: regular earnings (Table 38), casual earnings (Table 39),
self-employment earnings (Table 40) — all-industry only; job quality (Table 36) —
non-agriculture universe only; enterprise-size distribution (Table 37) — all-India only;
industry-level casual earnings (Table 51) — all-India only. RSEs are published only for
LFPR/WPR/UR and industry distributions, never for earnings or job-quality tables.
**Manufacturing-specific state earnings and job quality, with design-based standard errors
and intervals, are not published; Layer 4 is a genuine contribution.**

### ASI Summary Results and Volume I (MoSPI; verified on 2022–23, same architecture) — partial overlap

Already published at state level: **distribution of factories in operation by employment
size (Statements 13A/13B; 14A/14B for manufacturing only)** — official bands 0–14 … 5000+;
state × NIC2 GVA and emoluments **absolute totals** (Volume I Tables 2a, 4a). Ratios are
published only all-India-by-industry (Table 7, Statement 6) or all-industry-by-state
(Statements 9A/9B) — **never state × industry**. No composition-standardized comparison
exists (Statement 18 is a concentration table). Caveats: ASI 2023–24 full volumes could not
be confirmed online (site unscrapeable; results press-released 2025-08-27); whether
state-level *employment* (not factory counts) by size class is published was not confirmed.
**Project exhibits showing ASI factory-count size distributions must cite Statement 13A/14A;
the per-person ratios at state × NIC2 and the standardization are genuine contributions.**

### Tamil Nadu DES ASI report 2022–23 (pooled) — partial overlap

TN's own DES publishes "Report on ASI Tamilnadu 2022–23 (Pooled)": Table 4.10 "Principal
characteristics of Factories in Operation by size of workers" (a TN factory size-class
table on the finer pooled sample), district statements, TN × NIC totals (no ratios).
Different vintage (2022–23) and pooled frame, but it must be cited next to any TN factory
size-class exhibit.

### Tamil Nadu Economic Survey 2025–26 (State Planning Commission) — closest existing analysis; partial overlap

Published ~Feb 2026 at spc.tn.gov.in (supersedes the 2024–25 edition for this check):

- **Table 4.7 (p.97):** "Distribution of Manufacturing units, Employment, and GVA by size
  class for Tamil Nadu and All India, 2023–24" — **combines ASI and ASUSE into one
  distribution**, with Mehrotra & Giri (2019) size definitions (micro <10, small 10–19,
  medium 20–99) cited in footnote 13 (p.96). The missing-middle literature is therefore
  already invoked in an official TN document, though only to define bands.
- **Table 4.1 (p.87):** state-wise factories/employment/GVA rankings, 2023–24.
- **Table 4.11 (p.101):** large-factory (100+) employment share time series, TN vs Gujarat,
  Maharashtra, India, with an explicit "dual pattern" narrative (para 4.9.2).
- **Section 4.3 (pp.90–91):** TN's factory wage share of GVA ~15% vs Gujarat 8% and
  Maharashtra 9%; emoluments share 30% vs 18%/24% — **this anticipates the direction of the
  project's F3 labour-share finding.** F3's direction is corroborated, not novel; the
  project's specific additions are the 2023–24 per-paid-person levels across all six
  comparators and the composition-adjusted decomposition.

Not in the Economic Survey: a peer-state size-band comparison across the full 1-to-250+
range, survey-separated frames (4.7 merges them — the merge the project explicitly avoids),
suppression/uncertainty discipline, adjusted decompositions, or worker-side job quality by
state.

### Academic literature — contextual background (classified from the prior verified workflow)

- Hsieh & Olken (2014), "The Missing 'Missing Middle'": firm-size distributions in India,
  Indonesia, Mexico decline continuously with no discontinuity. Motivates the diagnostic;
  contains no TN or 2023–24 analysis.
- Hsieh & Klenow (2009; 2014): misallocation dispersion; Indian plants grow less with age.
  Background for interpretation only.
- Mehrotra & Giri (2019), "The size structure of India's enterprises: Not just the middle is
  missing": thematic predecessor; its size definitions are now in official TN use (ES Table
  4.7 footnote).
- NSS 73rd Round (2015–16): predecessor unincorporated-sector survey; different vintage.
- 2023 small-establishment (5–49 workers) and 2016 family-to-hired-labour papers: background.

### Udyam registration statistics — contextual background

TN's Udyam base is 98.16% micro (3,300,096 of 3,362,057 as of 2025-03-31). Registration
universe, not a survey estimate; usable as context only.

### TN policy documents — Layer 6 inputs, not overlapping analyses

MSME Policy Note 2025–26, Industrial Policy 2021, Budget Speech 2025–26: verified in
`LAYER6_POLICY_EVIDENCE_NOTES.md`. They state objectives, instruments and outputs; none
performs the project's statistical analysis.

## Consequences now binding on the storyboard and frontend

1. Never claim the project is the first size-class or labour-share analysis of TN
   manufacturing. Cite ES 2025–26 Chapter 4 (Tables 4.7, 4.11, §4.3) as the closest official
   analysis and position the project as the survey-separated, peer-benchmarked,
   uncertainty-disciplined complement.
2. Cite ASI Statement 13A/14A and TN DES Table 4.10 beside any factory size-class exhibit;
   cite ASUSE Tables 34/36 beside Layer 3 ASUSE overall values (which are gates, not
   findings).
3. F3's public wording may cite the ES only for the *direction* (TN's labour share highest
   among peers). The ES's levels (15%/30%) could not be reconciled with official ASI 2023-24
   totals, while ours reconcile almost exactly — see `EXTERNAL_VALIDATION.md` §5. Never cite
   the ES levels as corroboration.
4. The genuinely unpublished results — ASUSE state size distribution, state × NIC2
   per-person ratios, adjusted decompositions, manufacturing-specific worker outcomes with
   intervals — carry the novelty weight.
5. RESOLVED 2026-07-13: the ASI 2023–24 Summary Results were located on microdata.gov.in
   (catalog 256) and the project's per-return size distribution reconciles with Statement 14A
   near-exactly (100+ unit share 28.42% vs 28.43%); the equal-allocation series differs by
   the documented multi-unit adjustment, now quantified. Full register:
   `EXTERNAL_VALIDATION.md`.
