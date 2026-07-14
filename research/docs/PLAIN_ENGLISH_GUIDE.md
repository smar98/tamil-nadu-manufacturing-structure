# The whole project, explained from scratch

Written for a reader with no statistics background. It follows the site top to
bottom and decodes every term the site uses. Nothing here is new analysis —
every number quoted is on the site or in the research docs, and the site is the
canonical version.

---

## 1. The three surveys (why there are three, and why they never mix)

India has no single census of manufacturing. It measures the sector with three
separate surveys run by MoSPI (the Ministry of Statistics and Programme
Implementation), and each one can only see part of the picture:

- **ASI — Annual Survey of Industries.** Covers **registered factories**:
  units registered under the Factories Act (roughly, ≥10 workers with power or
  ≥20 without). It collects each factory's *books* — output, inputs, capital,
  wages — through an annual paper return. Tamil Nadu has ~29,899 of these.
- **ASUSE — Annual Survey of Unincorporated Sector Enterprises.** Covers the
  **unincorporated** economy: the tailor's shop, the grinding mill, the
  ten-person workshop — businesses that are not companies and not registered
  factories. Tamil Nadu has ~1.39 million of these in manufacturing.
- **PLFS — Periodic Labour Force Survey.** Visits **households**, not
  businesses, and asks *workers* about their jobs: earnings, contracts, paid
  leave, social security. It cannot see any establishment's books.

Why they never mix: the three surveys have no common identifier (no shared ID
that would let you match a PLFS worker to their ASI factory), and their
universes only partly overlap. So you cannot build a "firm ladder" where a
workshop grows into a factory — the same unit is never observed in two
surveys. Any analysis that stitches them into one series is quietly assuming
things the data cannot support. That is why every chart on the site names its
survey.

## 2. The headline measure: GVA per person

**GVA (gross value added)** = the value of what a factory ships out, minus the
materials and services it bought in. It is the value the factory itself
created — the pie available to pay workers, reward the owners' capital, and
reinvest.

**GVA per person engaged** divides that pie by everyone working in the factory
(employees, contract workers, working owners — the ASI term **persons
engaged** covers all of them). This is the measure on which Tamil Nadu, with
India's largest factory workforce (2.89 million people, 15 of every 100 Indian
factory workers), falls to the bottom of the big-state list: about ₹8.4 lakh
per person per year, versus ₹13.0 lakh in Gujarat and ₹15.4 lakh in
Maharashtra (2023-24, current rupees).

**Current rupees** means the values are in that year's prices, not adjusted
for inflation. Cross-state comparisons in the same year are unaffected; the
16-year persistence check compares *rankings* within each year, which is also
unaffected.

## 3. "Counting establishments" vs "counting jobs"

An **establishment** is a place of business — one workshop, one unit. When the
site says 65% of Tamil Nadu's unincorporated manufacturing establishments are
"one person working alone", that counts *places*. Counting **jobs** asks a
different question: what share of all the *people* work in places of each
size? Single-person units are 65% of places but only 32% of jobs, because a
20-person workshop counts once as a place but twenty times as jobs. Across
India the tilt is even stronger (72% of places, 43% of jobs) — tiny units
dominating the count of places is what the unincorporated sector looks like
everywhere, which is why it cannot be Tamil Nadu's special disease.

**Why the workshop chart says "not published" above 50 workers but the factory
chart later has numbers for 50–249:** two different surveys. Almost nothing
unincorporated is that big, so ASUSE's *sample* contains too few such units in
TN to estimate anything (fewer than 10 sampled units → we suppress). The ASI,
which samples registered factories, has plenty of mid-size units. The bands
look the same; the underlying data source has switched, and the site flags the
switch.

## 4. The missing middle (and why we tested it)

The **missing middle** is the decades-old diagnosis that India has lots of
tiny firms, a few giants, and abnormally few mid-size firms (Krueger 2009,
ICRIER; Mazumdar & Sarkar's books). It is also contested — Hsieh & Olken's
2014 *Journal of Economic Perspectives* paper "The Missing 'Missing Middle'"
argues the pattern largely dissolves when measured properly. Both sides are
cited on the site now.

Our test: define "the middle" four different ways (10–99, 10–249, 20–249,
50–249 workers) and compute the share of factory employment inside it for TN
and each peer. Under every definition, TN's middle is normal-or-deep next to
its peers. So whatever explains the value gap, a uniquely thin middle is not
it.

**The sizing wrinkle (equal-allocation vs per-return, Statement 14A):** one
ASI paper return can cover several factories under the same owner. To say "how
big is this factory" you must pick a rule. *Per-return* keeps the whole return
as one unit — this matches official practice, and our per-return numbers
reproduce **Statement 14A** (the official published ASI table of factories by
employment size) to 0.01 percentage points, which is how we know the machinery
is right. *Equal-allocation* splits the return's workers evenly across its
units — arguably closer to "establishments". The middle-diagnostic verdict is
the same under both, which is the point of showing both.

## 5. The fair test: the Kitagawa decomposition

The problem: Tamil Nadu makes garments; Gujarat makes petrochemicals. Chemical
plants generate more value per worker than garment factories anywhere on
earth. So a raw TN-vs-GJ comparison partly measures *what* each state makes,
not *how well* it makes it.

The tool: a **Kitagawa decomposition** (Kitagawa 1955 — the standard method,
also the ancestor of Oaxaca-Blinder). It splits an observed gap into:

- the **composition (industry-mix) component** — the part explained by the two
  states making different things, and
- the **within-industry component** — the part that remains when you compare
  the same industries with the same weights.

Mechanics, in one paragraph: take the broad industries both states actually
have (**common support**). For each industry, note each state's GVA per person
(the "rate") and its share of employment (the "weight"). Build a
counterfactual where both states get the *same* weights (we use the average of
the two states' weights — the "symmetric" choice, so neither state's mix is
treated as the norm). The gap that survives under common weights is the
within-industry component; the rest is mix. The two parts sum exactly to the
gap — the build checks that identity to zero on every row.

Result vs Gujarat: raw gap ≈ ₹4.6 lakh per person per year on common ground;
33% is mix (that part really was garments-vs-chemicals); **67% survives within
the same industries**. Against India, Maharashtra and Karnataka the within
share is similar or higher. We stress-tested this at 7 broad groups, 24
detailed industries, and industry-and-size jointly: the within component is
the majority of the gap in every specification (54–86%), TN trails in 16–22 of
~23 industries, and TN's aggregate rate has been below GJ/MH/KA in *every*
year 2008-09 to 2023-24. Details: `ROBUSTNESS_WITHIN_INDUSTRY.md`.

**"Two-digit industry level"**: industries are coded by the **NIC** (National
Industrial Classification). The first two digits give ~24 broad manufacturing
divisions — NIC 13 is textiles, NIC 26 is computers/electronics, NIC 27 is
electrical equipment. "Product mix below the two-digit level" means: within
NIC 13, one state might make basic yarn and the other technical textiles, and
the decomposition cannot see that. That, plus possible price differences, is
what "the same industries" can still hide — stated as an unprovable on the
site.

**Why one comparator at a time, never a league table:** each pairwise
comparison builds its own common ground and its own average weights. The
TN–GJ and TN–KA numbers are answers to *different* counterfactual questions,
so lining them up as a ranking would be comparing apples to constructed
oranges.

**Why these comparators:** India, the two states just behind TN on factory
employment (Gujarat and Maharashtra — also the top two on total value added),
and the three southern neighbours (Karnataka, Telangana, Kerala).

**Why Kerala shows "not published":** the decomposition is only published when
the retained common-support industries cover ≥95% of *both* states'
workforces. TN–Kerala fails that gate. Kerala stays visible because dropping a
comparator after seeing the results is cherry-picking.

**Why Telangana has no industry breakdown:** the raw TN–TG gap is tiny
(≈₹0.5 lakh). Decomposing a near-zero number splits noise, and the shares
come out silly (>100%). The site shows the raw comparison and says why it
stops there. Related: TN's factories *pay* more than TG's on the raw average,
but 97% of that pay advantage is industry mix — TN simply has more of the
industries that pay factory workers well.

**Capital, and the electronics exception:** **fixed capital per person** is
the machinery, buildings and equipment behind each worker. TN's factories
operate with roughly a third of Gujarat's and half of Maharashtra's and
Karnataka's — a real, measurable channel (less capital per worker generally
means less value per worker). But it cannot be the whole story: in electrical
and electronics manufacture TN holds 1.3–1.5× the capital per person of
GJ/MH/KA and still produces 32–45% less value per person. (One nuance kept in
the research docs: in *core* electronics, NIC 26 alone, Karnataka is an
exception — TN holds slightly less capital there, 0.87×.) High electronics
exports and low value added per worker are consistent: assembly-heavy
electronics imports expensive components, adds a thin slice of value, and
exports the expensive result.

## 6. The workers' slice

**Emoluments** is the ASI's word for everything the factory pays for labour:
wages, bonuses, and the employer's provident-fund and insurance contributions.
Our **labour-cost proxy** = emoluments + staff welfare spending (canteens,
housing, medical — welfare is not cash in hand, which is why the site calls
the measure "broader than take-home pay").

**Labour share** = labour-cost proxy ÷ GVA. Tamil Nadu's is 43.3% — the
highest among all comparators by 7.4 to 12.1 percentage points.

The arithmetic you (Sanchit) worked out on the voice note is exactly right,
and the site now states it your way: TN's workers are *not* paid more than
workers elsewhere (pay is near the national average); their ordinary pay is a
large fraction of the unusually small value their factories add. High share ×
small pie = middling pay. The labour share being highest is mostly a
reflection of the denominator (GVA) being small.

**Job quality** (PLFS): written contracts, paid leave, social security. TN
beats India, Gujarat and Kerala, and trails Karnataka and Telangana by 14–19
points. These are workers' own answers, so they carry proper confidence
intervals (below).

## 7. Uncertainty: SE, RSE, CI — and the 7.877% you spotted

- **Standard error (SE):** surveys interview a sample, not everyone, so every
  estimate would wobble if you drew a different sample. The SE measures that
  wobble.
- **RSE (relative standard error):** the SE as a percentage of the estimate.
  RSE 2.6% on an estimate of 100 means the wobble is about ±2.6.
- **95% confidence interval (CI):** roughly, estimate ± 2×SE — the range that
  would contain the true value in 95 of 100 repeated samples. The whiskers on
  the earnings and protections charts are these.

**The 7.877% in the ledger is not an RSE.** That row checks whether we could
*replicate MoSPI's own published RSE figure* for ASUSE TN all-activity GVA per
worker. MoSPI publishes 2.64; our replication gets 2.85; the difference
between those two numbers is 7.877%, inside the deliberately wide 15%
tolerance for that check (MoSPI's exact variance machinery uses listing data
that is not public, so perfect replication is impossible — we documented
that). The estimate's own sampling noise is the 2.64%, which is small. The
site's ledger now says this under the table, because your misreading was the
natural reading.

Related honesty rules: PLFS estimates get CIs (the survey's two-subsample
design supports them). ASI/ASUSE establishment-side estimates get none,
because the public files cannot support defensible ones — "we print no
interval we cannot defend." And the decomposition rows have no significance
tests, which is stated, not hidden.

## 8. Suppression (the hatched slots)

A cell is published only if it rests on **≥10 sampled units** and no single
unit carries **>70%** of the weighted total (for PLFS: ≥30 respondents, ≥10
first-stage units, effective sample ≥30, no weight >20%). Anything that fails
renders as a hatched slot labelled "not published (sample too small)" — never
as zero, and never reconstructable from other published numbers. The TN
Economic Survey publishes some ASUSE cells resting on ≤9 sampled
establishments; this project deliberately does not.

## 9. The reconciliation ledger (the 28 gates)

Before anything is published, the build recomputes 28 figures that the
government has *also* published — establishment counts, GVA per worker by
tier, PLFS shares, contract rates — and compares ours to theirs. If any check
fails, the tests fail and nothing ships. Where checks pass, they match within
2%, usually within a fraction of a percent. This is the project's core
credibility device: anyone can verify our totals against the government's own
tables before trusting the numbers the government has *not* published (the
decompositions).

One disclosed flag: Karnataka's published ASUSE emoluments figure sits 3.5%
from every estimator variant we tried. Both values are shown in the research
appendix; the site marks it "△ disclosed" rather than pretending it
reconciles.

## 10. The policy ledger

Source documents: MSME Policy Note 2025-26, Industries Policy Note 2025-26, TN
Economic Survey 2025-26, Industrial Policy 2021 (expired 31 March 2025;
successor announced June 2026, not yet published). The four instruments and
the **evidence ladder** on each card: *objective stated → instrument verified
→ output reported → outcome measured → impact known*. Every instrument stops
at "output reported" — the documents record what programmes aim at and
disburse, never what they cause. The site's claim is deliberately narrow: the
measured gaps (value per worker, pay levels, contract coverage) sit in one
place, and the stated objectives (getting bigger, hiring more, attracting
investment, credit volume) in another. That is a reading of stated objectives,
not an evaluation — and it is labelled as ours.

(Note: we date the policy documents rather than referencing the political
context; our evidence base ends at the 2025-26 Policy Notes and the June 2026
announcement.)

## 11. What the site never claims

- **No causality.** Every comparison is an association between survey
  aggregates from one year. "Is associated with" is the whole claim.
- **No firm dynamics.** Snapshots cannot see firms that tried to grow and
  failed.
- **No policy evaluation.** Nothing measures any subsidy against a
  counterfactual.
- **No merged surveys.** Ever.

## 12. Small mechanics

- **USD figures:** ₹83/USD, approximately the FY 2023-24 average market rate,
  rounded hard — for scale, not accounting.
- **Lakh / crore:** 1 lakh = 100,000; 1 crore = 10 million; ₹1 lakh crore =
  ₹1 trillion ≈ $12 billion.
- **Where things live:** methods in `research/docs/METHODOLOGY.md`; the
  robustness battery in `ROBUSTNESS_WITHIN_INDUSTRY.md`; external checks in
  `EXTERNAL_VALIDATION.md`; the payload the site reads is
  `public/data/manufacturing-structure.json`; raw survey microdata stays local
  and is never committed.
