# Layer 6 findings ledger

Laundry list of empirical findings available for the Layer 6 policy-evidence matrix and the
final narrative. All numbers are read directly from the canonical Layers 1–5 payload
(`public/data/manufacturing-structure.json`, SHA-256 `a4fd25ae…`). Nothing is cut yet; the
Status column records current intent and can be revised. Every finding is descriptive; none
identifies a cause. Gaps are Tamil Nadu minus comparator, 2023–24, current prices.

Peers: GJ Gujarat, MH Maharashtra, KA Karnataka, TG Telangana; KL Kerala is a sensitivity
comparator. "Mix" = share of the common-support raw gap attributed to the industry-composition
component in the Layer 5 pairwise decomposition (not comparable across comparators as a
league table).

## Approved headline candidates (user review 2026-07-13: keep all)

| # | Finding | Key numbers | Mapped instrument | Status |
|---|---|---|---|---|
| F1 | No obvious missing middle under the tested definitions and peer set | Layer 1/2 diagnostic; TN 10–249 employment share not abnormally low vs peers. Novelty tempered (see EXISTING_ANALYSIS_VERIFICATION.md): ES 2025–26 Table 4.7 publishes a merged-frame TN size-class table for 2023–24 and cites Mehrotra & Giri; ASI Statements 13A/14A and TN DES Table 4.10 publish factory size distributions. The survey-separated full-range peer diagnostic remains unpublished | Additional capital subsidy for scaling up | Headline |
| F2 | Registered-factory GVA per person engaged is far below every peer except Telangana, and the gap is mostly within-industry | TN ₹839,770; gaps: IN −390,628, GJ −464,902, MH −696,755, KA −654,054, TG −45,797, KL −312,838. Industry mix explains 16–33% vs IN/GJ/MH/KA; within-industry gap dominates | Investment incentives; sector programmes | Headline |
| F3 | Factory pay trails peers but labour's share of GVA is higher than every comparator ("larger slice of a smaller pie") | Emoluments per paid person: TN ₹316,681; IN −51,520, GJ −53,449, MH −180,831, KA −133,026, TG +29,455, KL −26,689. Labour-cost-proxy share of GVA: TN 43.3%, +7.4 to +12.1pp vs all six comparators. TN's pay advantage over TG is 97% industry mix. Direction corroborated by TN Economic Survey 2025–26 §4.3 (TN factory wage share ~15% vs GJ 8%, MH 9%); must be cited — the levels, six-comparator panel and adjusted decomposition are the project's additions | Wage/job-quality relevance of investment and sector instruments | Headline |
| F4 | Worker-side job quality splits the peer set: TN beats IN/GJ/KL, trails KA and TG by double digits | Written contract TN 50.4% (KA −17.6pp, TG −14.3pp); paid leave TN 54.9% (KA −16.1pp, TG −13.7pp); specified social security TN 53.4% (KA −15.3pp, TG −19.0pp) | EPF payroll subsidy (>20 employees) | Headline |
| F5 | Regular monthly manufacturing earnings are middling | TN ₹17,277; ≈ India (+187), GJ +412, MH −3,701, KA −1,500, TG −5,523, KL −2,127 | Context for payroll/formalisation instruments | Headline |
| F6 | 20-worker threshold diagnostic: employment structure around the payroll-subsidy threshold plus social-security coverage by enterprise size | Layer 1 bands 10–19/20–49; Layer 4 job quality by PLFS enterprise size. Explicitly a threshold diagnostic, not an evaluation | EPF payroll subsidy | Headline |
| F7 | The unincorporated sector is a relative strength | ASUSE GVA per worker TN ₹133,244: IN +19,044, KA +13,928, TG +13,516, GJ −9,775, MH −5,891, KL −54,155. Hired-worker emoluments TN ₹140,586 mid-pack: IN +3,574, KA +8,839, GJ −11,911, MH −5,355, TG −23,626, KL −39,850 | MSME lending; livelihood instruments; hook for ASUSE problems appendix | Headline |
| F8 | Expired Industrial Policy 2021 targets vs current instruments | 2021 targets (p.4) historical; validity to 31 Mar 2025 (p.7); successor check pending (web verification in progress) | Frames the whole matrix | Headline |

## Secondary findings (keep in the list; likely supporting text or appendix)

| # | Finding | Key numbers | Status |
|---|---|---|---|
| S1 | Self-employment gross earnings are a TN strength | TN ₹15,589/30 days: above IN +4,030, GJ +1,442, KA +3,823, TG +6,544, KL +1,574; below only MH −2,369. Concept: gross, includes returns to capital/ownership | Secondary |
| S2 | Casual person-day earnings are mid-pack with a large Kerala gap | TN ₹497/day: IN +54, GJ +103, MH +49, KA −24, TG −45, KL −258 | Secondary |
| S3 | Kerala's pattern is the mirror of TN's factory story | KL leads TN in unincorporated GVA per worker (+54k) and hired-worker pay (+40k) and casual wages, with smaller factories (53.9 persons/factory) | Secondary / sensitivity framing |
| S4 | TN–Telangana contrasts are heavily compositional | TG emoluments gap 97% mix; TG GVA gap has negative mix share (−31%): TN's industry mix flatters the raw comparison | Secondary / methods callout |
| S5 | ASUSE industry-adjusted gaps stay close to raw gaps | e.g. GVA per worker vs GJ: raw −9,775, within −4,381 (mix 42%); vs KA: within +14,054 (mix 3%) | Secondary |
| S6 | TN has high employer incidence in the unincorporated sector | TN HWE share 19.59% is canonical (payload `headline.hired_worker_share`). The India 11.7% and peer comparators are prior-session estimates NOT in the canonical payload; do not publish the comparison unless the builder adds peer HWE shares (out of Layer 6 scope) | Secondary — TN level usable; comparison not yet publishable |

## Planned appendix (approved 2026-07-13)

| # | Item | Notes |
|---|---|---|
| A1 | ASUSE reported-problems exploratory appendix | BUILT and sample-verified 2026-07-13 (`research/docs/LAYER6_ASUSE_PROBLEMS_APPENDIX.md`, `research/derived/asuse_problems_appendix.json`). Headline pattern: establishments reporting labour/skills/technology problems are far more registered, ICT-using, credit-using and higher-GVA than non-reporters — opposite of a naive binding-constraint signature, consistent with selection. E.g. skilled-labour reporters: 82.8% registered vs 38.1%, GVA/worker ₹201k vs ₹129k (n=379). Cross-sectional associations only; endogeneity caveat mandatory. TN ASUSE has <10 sampled manufacturing establishments above 49 workers, so size-group cells 50-249 and 250+ are suppressed |

## Interpretation boundaries binding on every entry

- Descriptive only; no causal claims about industry, size, policy, productivity or growth.
- Adjusted comparator rows are pairwise and must not be ranked as a league table.
- Policy documents establish stated objectives, instruments and outputs (evidence-ladder
  levels 1–3); survey results describe some level-4 outcomes; level-5 impact is out of scope.
- Suppressed cells stay suppressed; no residual reconstruction.
