# Public-site storyboard (v1)

Authoritative narrative specification for the frontend rebuild, per the handoff's
storyboarding gate. Each section specifies: the public question, the one empirical claim its
exhibit supports, the denominator and statistical unit, the comparison geography, the caveat
placed next to the claim, and the transition. Implementation (Next.js) may be delegated;
headlines and claims may not be invented or strengthened during implementation. The final
claim audit checks the built site against this file, the canonical payload and
`EXISTING_ANALYSIS_VERIFICATION.md`.

Global rules: outcomes lead, structure explains. Every number displayed must exist in the
canonical payload (SHA `a4fd25ae…`) or the appendix JSON. Every exhibit shows unweighted
sample counts where the payload provides them, marks suppressed cells as unavailable (never
zero), and carries the survey-universe label. Layer 5 adjusted rows are never ranked across
comparators. Citation duties from `EXISTING_ANALYSIS_VERIFICATION.md` §"Consequences" are
mandatory. No causal wording anywhere: gaps are "associated with", never "caused by".

---

## Section 0 — Headline

- **Public question:** What did we find about Tamil Nadu's manufacturing economy?
- **One claim:** Tamil Nadu's manufacturing structure is not the problem the missing-middle
  hypothesis expects; its registered factories generate less value per person than every
  major peer except Telangana even within comparable industries, while its workers' job
  quality beats most of India but trails Karnataka and Telangana.
- **Denominator/unit:** none displayed; text-only synthesis of the three exhibits below.
- **Comparison geography:** India, Gujarat, Maharashtra, Karnataka, Telangana (Kerala as
  labelled sensitivity).
- **Caveat beside claim:** "Descriptive comparisons from three separate surveys, 2023–24.
  Nothing here identifies causes or evaluates any policy."
- **Transition:** "To see why these three findings hold, start with what each survey can and
  cannot see."
- **Outcome emphasis:** the within-industry GVA gap (F2) and the job-quality split (F4) are
  the two headline outcomes, per the locked priority on outcomes.
- **Policy evidence vs interpretation:** none in this section.

## Section 1 — Three surveys, three views

- **Public question:** What data can actually see Tamil Nadu's manufacturing economy?
- **One claim:** ASUSE, ASI and PLFS observe three different populations — unincorporated
  establishments, registered factory returns, and workers — that cannot be merged into one
  firm ladder.
- **Denominator/unit:** none; definitional diagram (universe, unit, weight, reference
  period per survey).
- **Comparison geography:** none.
- **Caveat:** "A return in ASI can cover more than one factory; PLFS reports where workers
  say they work. No establishment can be followed between surveys."
- **Transition:** "Within each lens separately, here is where Tamil Nadu's manufacturing
  establishments and jobs actually sit."
- **Note:** cite that the TN Economic Survey 2025–26 (Table 4.7) combines ASI and ASUSE into
  one size table; state plainly that this site deliberately keeps them separate and why.
- **Policy evidence vs interpretation:** none.

## Section 2 — The complete size structure (Layer 1/2)

- **Public question:** Where are Tamil Nadu's manufacturing establishments and jobs, by size?
- **One claim:** Tamil Nadu's unincorporated manufacturing is overwhelmingly tiny (with a
  relatively high employer share of 19.6%), while registered-factory employment is
  concentrated in large units — with establishment shares and employment shares telling
  different stories.
- **Denominator/unit:** ASUSE establishments and workers; ASI returns (equal-allocation
  approximation) and persons engaged. Shares of each survey's own manufacturing total.
- **Comparison geography:** Tamil Nadu; India shown as reference distribution.
- **Caveat:** "ASI size uses persons engaged divided by reported units — an approximation
  when a return covers several units (per-return sensitivity in methods). ASUSE Tamil Nadu
  cells above 49 workers are suppressed for sample-size reasons."
- **Transition:** "Small establishments dominating counts is normal everywhere. The real
  question is whether Tamil Nadu's middle is unusually thin."
- **Citations beside exhibit:** ASI Statement 13A/14A, TN DES Table 4.10, ES 2025–26 Table
  4.7 (as the merged-frame official view).
- **Policy evidence vs interpretation:** none.

## Section 3 — Is Tamil Nadu unusual? (missing-middle diagnostic, F1)

- **Public question:** Does Tamil Nadu lack middle-sized manufacturing?
- **One claim:** Under four predeclared middle definitions and a predeclared peer set, Tamil
  Nadu's middle-size employment share shows no obvious abnormal shortfall.
- **Denominator/unit:** share of survey-estimated manufacturing employment (per survey,
  never combined) in each middle band.
- **Comparison geography:** India, all available States/UTs (distribution), the four core
  peers, Kerala flagged sensitivity.
- **Caveat:** "A diagnostic, not proof of health: it cannot see establishments that wanted
  to grow and could not. Suppressed cells make some ASUSE definitions unavailable."
- **Transition:** "If size structure is not obviously unusual, the peer differences that
  remain must live in what establishments produce and what workers get."
- **Outcome emphasis:** none (structural section).
- **Policy evidence vs interpretation:** evidence — the scale-up capital subsidy exists
  (Policy Note p.37); interpretation, clearly labelled — statewide size scarcity alone does
  not justify it, and this analysis cannot test its other justifications.

## Section 4 — Which industries create the pattern (Layer 2)

- **Public question:** Which industries hold Tamil Nadu's manufacturing jobs?
- **One claim:** Tamil Nadu's manufacturing employment is concentrated in [top NIC2 groups
  from payload — implementation reads values from `industry_employment` /
  `size_industry_employment`], and this mix differs enough from peers to distort naive
  comparisons.
- **Denominator/unit:** share of each survey's manufacturing employment by NIC2 and size ×
  NIC2.
- **Comparison geography:** Tamil Nadu vs India (payload scope for this table).
- **Caveat:** "Industry mix is why raw state comparisons mislead — the adjustment in
  Section 6 exists because of this table."
- **Transition:** "Now the outcomes: first what establishments generate and pay, then what
  workers report."
- **Policy evidence vs interpretation:** none.

## Section 5 — Establishment outcomes (Layer 3; F2, F3, F7)

- **Public question:** How much value do Tamil Nadu's manufacturers generate, and what do
  they pay?
- **One claim (factories):** Registered-factory GVA per person engaged (₹8.4 lakh) trails
  every core peer except Telangana; emoluments per paid person follow the same order — yet
  labour costs take a larger share of GVA in Tamil Nadu than in any comparator.
- **One claim (unincorporated):** ASUSE GVA per worker and hired-worker emoluments are
  mid-pack or better — the unincorporated sector is a relative strength, not the weak spot.
- **Denominator/unit:** ASI persons engaged / paid persons engaged (per return aggregates);
  ASUSE workers in market establishments / hired workers in HWEs. Ratios of weighted totals,
  current rupees, 2023–24.
- **Comparison geography:** India + four core peers + Kerala (sensitivity).
- **Caveat:** "GVA per person is not efficiency or welfare: capital intensity, product mix,
  prices and markups all move it. The labour-share *direction* (Tamil Nadu highest among
  peers) is consistent with official ASI 2023–24 totals and with the TN Economic Survey
  2025–26 (§4.3); the Survey's published share levels use a base it does not specify and are
  not comparable with the levels shown here (see External Validation §5)."
- **Transition:** "Establishment accounts say what is produced and paid out. Workers say
  what they actually receive."
- **Outcome emphasis:** F3's "larger slice of a smaller pie" is this section's memorable
  line — always with the ES corroboration citation.
- **Policy evidence vs interpretation:** evidence — no verified current instrument states a
  wage-level or labour-share objective; interpretation, labelled — this is a gap between
  measured outcomes and stated policy objectives, not a policy failure claim.

## Section 6 — Worker outcomes and the fair comparison (Layers 4–5; F4, F5, F6, S1, S2)

- **Public question:** What do Tamil Nadu's manufacturing workers earn and get — and do the
  peer gaps survive an apples-to-apples industry comparison?
- **One claim (workers):** Regular manufacturing earnings are middling; job quality (written
  contracts 50.4%, paid leave 54.9%, specified social security 53.4%) beats India, Gujarat
  and Kerala but trails Karnataka and Telangana by double digits.
- **One claim (adjusted):** The factory GVA and pay gaps against Gujarat, Maharashtra and
  Karnataka are mostly within-industry (composition explains 16–33%); against Telangana the
  pay advantage is almost entirely industry mix.
- **Denominator/unit:** PLFS persons / person-days (three earnings concepts kept separate,
  each with its recall period and design-based 95% interval); Layer 5 standardized rates per
  outcome-specific person denominator.
- **Comparison geography:** India + four core peers + Kerala (sensitivity); pairwise
  adjusted rows shown one comparator at a time — never as a ranked table.
- **Caveat:** "Earnings concepts are not comparable with each other or with establishment
  emoluments. Adjusted gaps are composition controls with no confidence intervals (component
  variances unavailable), and a persisting within-industry gap has no identified cause."
- **Transition:** "These are the demonstrated gaps. The last section asks what the state's
  current policy instruments say about them."
- **Outcome emphasis:** this is the emotional centre of the site per the user's priority —
  job quality (F4) gets the largest visual weight.
- **Policy evidence vs interpretation:** none here; deferred to Section 7.

## Section 7 — Findings and instruments (Layer 6)

- **Public question:** What is the state already doing about any of this?
- **One claim:** Tamil Nadu's verified current instruments target investment, MSME category
  graduation, EPF-covered hiring past 20 workers and sectoral development — none states an
  objective for wage levels, labour share, written contracts or paid leave, which is where
  several measured peer gaps sit.
- **Denominator/unit:** none; the matrix from `LAYER6_EVIDENCE_MAP.md` rendered as
  finding → instrument → what government reports → what remains unknown.
- **Comparison geography:** n/a.
- **Caveat:** "Documents establish objectives, instruments and outputs — not take-up, demand
  or impact. The Industrial Policy 2021 targets expired 31.03.2025; as of July 2026 no
  successor is notified (a new policy was announced as intent in June 2026)."
- **Transition:** closes into the methods drawer.
- **Policy evidence vs interpretation:** the matrix separates columns explicitly; the
  "findings without a matching instrument" row is interpretation and is labelled as the
  project's reading, with the evidence cells quoting documents verbatim with printed page
  references.

## Section 8 — Methods drawer (collapsed)

Survey definitions, estimands, disclosure rules, uncertainty methods, the Layer 5 formulas,
the ES 2025–26 / ASI / DES citation notes, reproducibility pointer, and the exploratory
ASUSE problems appendix (association-only wording, endogeneity caveat, suppressed upper size
groups). The appendix never appears in the main narrative.

---

## Deferred / explicitly out of v1

Combined ASUSE–ASI size histogram (only the labelled approximation may appear in methods);
any causal or evaluative wording; any earnings-by-enterprise-size table; adjusted PLFS
comparisons; league-table renderings of Layer 5; interviews-dependent decision-tool claims;
`public/og.png` must be replaced during implementation (it belongs to another project).
