/* India's Factory State — server-rendered narrative site.
   Every number on this page is read at build time from the canonical payload
   (public/data/manufacturing-structure.json), the committed ASI panel
   (research/derived/asi_aggregates.csv) or the ASUSE problems appendix. Nothing
   is a hand-typed statistic; citation text referencing official published
   tables follows research/docs/EXTERNAL_VALIDATION.md. */

import fs from "node:fs";
import path from "node:path";
import payloadJson from "../public/data/manufacturing-structure.json";
import appendixJson from "../research/derived/asuse_problems_appendix.json";
import { CountUp, Scrolly, SectionNav, Tabs } from "./scrolly";

// ---------------------------------------------------------------------------
// Types (lean views over structure_v1)
// ---------------------------------------------------------------------------

type Stability = "stable" | "low_precision" | "suppressed";

type SizeRow = {
  survey: string;
  geography_id: string;
  classification: string;
  size_band: string;
  size_band_label: string;
  stability: Stability;
  suppression_reason: string | null;
  unit_share: number | null;
  employment_share: number | null;
  sample_count: number;
};

type MiddleRow = {
  survey: string;
  geography_id: string;
  geography_label: string;
  classification: string;
  middle_definition: string;
  middle_definition_label: string;
  stability: Stability;
  employment_share: number | null;
};

type ValueRow = {
  survey: string;
  dimension: string;
  geography_id: string;
  geography_label: string;
  concept?: string;
  per_person_value: number | null;
  stability: string;
  sample_count: number;
  labour_cost_proxy_share_of_gva?: number | null;
};

type PersonRow = {
  concept: string;
  dimension: string;
  geography_id: string;
  geography_label: string;
  estimate: number | null;
  ci95_lower: number | null;
  ci95_upper: number | null;
  stability: Stability;
  sample_count: number;
};

type AdjComponent = {
  cell_id: string;
  cell_label: string;
  tn_cell_rate: number;
  comparator_cell_rate: number;
  common_weight: number;
};

type AdjRow = {
  survey: string;
  outcome: string;
  adjustment_dimension: string;
  comparator_id: string;
  comparator_label: string;
  stability: string;
  suppression_reason: string | null;
  common_support_tn: number | null;
  common_support_comparator: number | null;
  common_support_raw_gap: number | null;
  composition_component: number | null;
  within_component: number | null;
  retained_cell_count: number;
  total_cell_count: number;
  tn_denominator_coverage: number;
  comparator_denominator_coverage: number;
  components: AdjComponent[];
};

type RawPeerRow = {
  outcome: string;
  comparator_id: string;
  comparator_label: string;
  tn_estimate: number | null;
  comparator_estimate: number | null;
  absolute_gap: number | null;
  stability: string;
};

type ValidationCheck = {
  check: string;
  reconstructed: number;
  published: number;
  relative_error?: number | null;
  absolute_error?: number | null;
  status: string;
};

type Payload = {
  meta: { price_basis: string; comparison_warning: string; disclosure: string };
  headline: {
    unincorporated_establishments: number;
    registered_factories: number;
    hired_worker_share: number;
  };
  plfs: { sample_workers: number; manufacturing_share: number };
  validation: ValidationCheck[];
  sources: { id: string; title: string; coverage: string; use: string; url: string; tables: string }[];
  structure_v1: {
    establishment_size: SizeRow[];
    middle_diagnostic: MiddleRow[];
    value_addition: ValueRow[];
    establishment_compensation: ValueRow[];
    worker_earnings: PersonRow[];
    worker_job_quality: PersonRow[];
    peer_comparisons_raw: RawPeerRow[];
    peer_comparisons_adjusted: AdjRow[];
    size_bands: { id: string; label: string }[];
    metadata: Record<string, Record<string, string>>;
  };
};

const payload = payloadJson as unknown as Payload;
const sv = payload.structure_v1;
const appendix = appendixJson as unknown as {
  reporting_shares: { category_label: string; dimension: string; value: number | null; stability: string }[];
};

// ---------------------------------------------------------------------------
// Build-time data assembly
// ---------------------------------------------------------------------------

const PEERS = ["IN", "24", "27", "29", "36", "32"] as const;
const NOT_PUBLISHED = "not published (sample too small)";

function readAsiPanel() {
  const raw = fs.readFileSync(
    path.join(process.cwd(), "research", "derived", "asi_aggregates.csv"),
    "utf8",
  );
  const [headerLine, ...lines] = raw.trim().split(/\r?\n/);
  const header = headerLine.split(",");
  const col = (name: string) => header.indexOf(name);
  const year = col("year");
  const state = col("state");
  const sector = col("sector_id");
  const employees = col("employees");
  const gva = col("gva");
  const fixedCapital = col("fixed_capital");
  const rows = lines.map((line) => line.split(","));
  const allMfg2023 = rows.filter((r) => r[year] === "2023" && r[sector] === "all-manufacturing");
  const tnPersons = Math.round(Number(allMfg2023.find((r) => r[state] === "33")![employees]));
  const indiaPersons = allMfg2023.reduce((sum, r) => sum + (Number(r[employees]) || 0), 0);
  const maxPersons = Math.max(...allMfg2023.map((r) => Number(r[employees]) || 0));
  // Persistence: is TN's GVA/person engaged below GJ/MH/KA in every complete panel year?
  const years = [...new Set(rows.filter((r) => r[sector] === "all-manufacturing").map((r) => r[year]))].sort();
  const rate = (y: string, s: string) => {
    const row = rows.find((r) => r[year] === y && r[state] === s && r[sector] === "all-manufacturing");
    return row && Number(row[employees]) > 0 ? Number(row[gva]) / Number(row[employees]) : null;
  };
  const alwaysBelow = ["24", "27", "29"].every((peer) =>
    years.every((y) => {
      const tn = rate(y, "33");
      const other = rate(y, peer);
      return tn !== null && other !== null && tn < other;
    }),
  );
  // Electronics beat: TN's capital and value per person in electrical &
  // electronics manufacture, relative to GJ/MH/KA, from the same panel.
  const per = (s: string, sec: string, num: number) => {
    const row = rows.find((r) => r[year] === "2023" && r[state] === s && r[sector] === sec);
    return row && Number(row[employees]) > 0 ? Number(row[num]) / Number(row[employees]) : null;
  };
  const elecPeers = ["24", "27", "29"].map((peer) => ({
    capitalRatio: per("33", "electrical-electronics", fixedCapital)! / per(peer, "electrical-electronics", fixedCapital)!,
    valueShortfall: 1 - per("33", "electrical-electronics", gva)! / per(peer, "electrical-electronics", gva)!,
  }));
  const elec = {
    capitalMin: Math.min(...elecPeers.map((p) => p.capitalRatio)),
    capitalMax: Math.max(...elecPeers.map((p) => p.capitalRatio)),
    shortfallMin: Math.min(...elecPeers.map((p) => p.valueShortfall)),
    shortfallMax: Math.max(...elecPeers.map((p) => p.valueShortfall)),
  };
  return { tnPersons, indiaPersons, maxPersons, alwaysBelow, elec, firstYear: years[0], lastYear: years[years.length - 1] };
}

const panel = readAsiPanel();
const perHundred = Math.round((panel.tnPersons / panel.indiaPersons) * 100);
const tnIsFirst = panel.tnPersons === panel.maxPersons;

const asiOverall = sv.value_addition.filter(
  (row) => row.survey === "asi" && row.dimension === "overall" && (PEERS as readonly string[]).concat("33").includes(row.geography_id),
);
const gvaPerPerson = (id: string) => asiOverall.find((row) => row.geography_id === id)!.per_person_value!;
const rankRows = [...asiOverall]
  .filter((row) => row.per_person_value !== null)
  .sort((a, b) => b.per_person_value! - a.per_person_value!)
  .map((row) => ({
    id: row.geography_id,
    label: row.geography_label,
    value: row.per_person_value!,
    n: row.sample_count,
  }));

const adjIndustry = new Map(
  sv.peer_comparisons_adjusted
    .filter((row) => row.survey === "asi" && row.outcome === "gva_per_person_engaged" && row.adjustment_dimension === "industry")
    .map((row) => [row.comparator_id, row]),
);
const adjIndustrySize = new Map(
  sv.peer_comparisons_adjusted
    .filter((row) => row.survey === "asi" && row.outcome === "gva_per_person_engaged" && row.adjustment_dimension === "industry_size")
    .map((row) => [row.comparator_id, row]),
);
const gj = adjIndustry.get("24")!;

const labourShareRows = sv.establishment_compensation
  .filter(
    (row) =>
      row.survey === "asi" &&
      row.concept === "labour_cost_proxy" &&
      row.dimension === "overall" &&
      (PEERS as readonly string[]).concat("33").includes(row.geography_id) &&
      row.labour_cost_proxy_share_of_gva != null,
  )
  .map((row) => ({
    id: row.geography_id,
    label: row.geography_label,
    value: row.labour_cost_proxy_share_of_gva!,
    n: row.sample_count,
  }))
  .sort((a, b) => b.value - a.value);

const overallPersonRows = (rows: PersonRow[], concept: string) =>
  rows
    .filter((row) => row.concept === concept && row.dimension === "overall" && (PEERS as readonly string[]).concat("33").includes(row.geography_id))
    .sort((a, b) => (b.estimate ?? -1) - (a.estimate ?? -1));

const asuseRawGva = sv.peer_comparisons_raw.filter((row) => row.outcome === "gva_per_worker");
const tnAsuseGva = asuseRawGva[0]?.tn_estimate ?? null;

const earningsConcepts = [
  { id: "regular_monthly_earnings", label: "Regular salaried work", unit: "₹ per month", recall: "preceding calendar month" },
  { id: "self_employment_30_day_gross_earnings", label: "Self-employment (gross)", unit: "₹ per 30 days", recall: "last 30 days" },
  { id: "casual_person_day_earnings", label: "Casual labour", unit: "₹ per person-day", recall: "previous 7 days" },
];
const jobConcepts = [
  { id: "written_contract", label: "Has a written job contract" },
  { id: "paid_leave", label: "Is eligible for paid leave" },
  { id: "specified_social_security", label: "Has a specified social-security benefit" },
];

const tnJob = (concept: string) =>
  sv.worker_job_quality.find((row) => row.concept === concept && row.dimension === "overall" && row.geography_id === "33")!;
const tnEarn = sv.worker_earnings.find(
  (row) => row.concept === "regular_monthly_earnings" && row.dimension === "overall" && row.geography_id === "33",
)!;

const problemsOverall = appendix.reporting_shares.filter((row) => row.dimension === "overall" && row.value !== null);
const maxProblemShare = Math.max(...problemsOverall.map((row) => row.value!));

// ---------------------------------------------------------------------------
// Formatting
// ---------------------------------------------------------------------------

const lakh = (value: number) => {
  const l = value / 100000;
  const digits = l >= 10 ? 1 : 1;
  return `₹${l.toFixed(digits)} lakh`;
};
const rupees = (value: number) => `₹${Math.round(value).toLocaleString("en-US")}`;
/* US dollar equivalents for international readers, ₹83 to the dollar
   (approximately the 2023-24 average market rate; noted in the colophon).
   Rounded hard — these are for scale, not accounting. */
const USD_RATE = 83;
const usd = (value: number) => {
  const dollars = value / USD_RATE;
  if (dollars >= 1e9) return `$${(dollars / 1e9).toFixed(0)} billion`;
  if (dollars >= 1e6) return `$${(dollars / 1e6).toFixed(0)} million`;
  const rounded = dollars >= 10000 ? Math.round(dollars / 100) * 100 : dollars >= 1000 ? Math.round(dollars / 10) * 10 : Math.round(dollars);
  return `$${rounded.toLocaleString("en-US")}`;
};
const lakhUsd = (value: number) => `${lakh(value)} (${usd(value)})`;
const rupeesUsd = (value: number) => `${rupees(value)} (${usd(value)})`;
const pct = (proportion: number, digits = 1) => `${(proportion * 100).toFixed(digits)}%`;
const pp = (proportion: number) => (proportion * 100).toFixed(1);
const int = (value: number) => Math.round(value).toLocaleString("en-US");
const covLabel = (row: AdjRow) => {
  const min = Math.min(row.tn_denominator_coverage, row.comparator_denominator_coverage);
  return min >= 0.9995 ? "all" : `at least ${pct(min, 1)}`;
};

// ---------------------------------------------------------------------------
// Shared page furniture
// ---------------------------------------------------------------------------

function Recon({ items, flag }: { items: string[]; flag?: string }) {
  return (
    <p className="recon">
      <span className={`mark ${flag ? "flagged" : "pass"}`}>{flag ? "△ disclosed" : "✓ checked"}</span>
      {items.map((item) => (
        <span key={item}>{item}</span>
      ))}
      {flag && <span>{flag}</span>}
    </p>
  );
}

function Exhibit({
  title,
  sub,
  children,
}: {
  title: string;
  sub?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="exhibit">
      <p className="exhibit-title">{title}</p>
      {sub && <p className="exhibit-sub">{sub}</p>}
      {children}
    </div>
  );
}

function HowWeKnow({ children }: { children: React.ReactNode }) {
  return (
    <details className="howweknow">
      <summary>How we know — the full technical detail</summary>
      <div className="howweknow-body">{children}</div>
    </details>
  );
}

function Hatch({ id }: { id: string }) {
  return (
    <defs>
      <pattern id={id} width="6" height="6" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
        <rect width="6" height="6" fill="var(--paper-recessed)" />
        <line x1="0" y1="0" x2="0" y2="6" stroke="var(--ink-3)" strokeWidth="1" />
      </pattern>
    </defs>
  );
}

// ---------------------------------------------------------------------------
// Exhibit: ranked strip (Act I)
// ---------------------------------------------------------------------------

function RankStrip({ annotated }: { annotated: boolean }) {
  const W = 720;
  const rowH = 48;
  const left = 128;
  const right = 96;
  const H = rankRows.length * rowH + 46;
  const max = rankRows[0].value;
  const x = (value: number) => left + (value / max) * (W - left - right);
  const mh = rankRows.find((row) => row.id === "27")!;
  const tn = rankRows.find((row) => row.id === "33")!;
  return (
    <figure className="dense-chart" role="img" aria-label={`Ranked strip of gross value added per person engaged, 2023-24: ${rankRows.map((r) => `${r.label} ${lakh(r.value)}`).join(", ")}.`}>
      <svg aria-hidden="true" focusable="false" viewBox={`0 0 ${W} ${H}`}>
        <line className="axis-line" x1={left} y1={10} x2={left} y2={H - 30} />
        {rankRows.map((row, index) => {
          const isTn = row.id === "33";
          const y = 26 + index * rowH;
          return (
            <g key={row.id}>
              <line className="gridline" x1={left} y1={y} x2={x(row.value)} y2={y} />
              <text x={left - 10} y={y + 4} textAnchor="end" fontSize="14" fontWeight={isTn ? 600 : 400} fill={isTn ? "var(--tn)" : "var(--grey-text)"}>
                {row.label}
              </text>
              <circle cx={x(row.value)} cy={y} r={isTn ? 9 : 7} fill={isTn ? "var(--tn)" : "var(--grey-fill)"} />
              <text x={x(row.value) + 14} y={y + 4} fontSize="13" fill={isTn ? "var(--tn)" : "var(--grey-text)"} fontWeight={isTn ? 600 : 400}>
                {lakh(row.value)}
              </text>
            </g>
          );
        })}
        {annotated && (
          <g>
            <line
              x1={x(tn.value)}
              y1={26 + rankRows.indexOf(tn) * rowH - 20}
              x2={x(mh.value)}
              y2={26 + rankRows.indexOf(tn) * rowH - 20}
              stroke="var(--tn)"
              strokeWidth="1.5"
              strokeDasharray="4 3"
            />
            <text
              x={(x(tn.value) + x(mh.value)) / 2}
              y={26 + rankRows.indexOf(tn) * rowH - 28}
              textAnchor="middle"
              fontSize="13"
              fontWeight="600"
              fill="var(--tn)"
            >
              {lakh(mh.value - tn.value)} short of Maharashtra, per person, per year
            </text>
          </g>
        )}
        <text x={left} y={H - 8} fontSize="12" fill="var(--ink-3)">
          Gross value added per person engaged, registered factories, 2023-24 · current rupees
        </text>
      </svg>
    </figure>
  );
}

// ---------------------------------------------------------------------------
// Exhibit: ASUSE size structure (Act III)
// ---------------------------------------------------------------------------

function SizeBars({ showJobs, showIndia }: { showJobs: boolean; showIndia?: boolean }) {
  const bandRows = (geo: string) =>
    sv.establishment_size.filter(
      (row) => row.survey === "asuse" && row.geography_id === geo && row.classification === "reported_establishment_workers",
    );
  const bandOrder = sv.size_bands.map((band) => band.id);
  const byBand = (rows: SizeRow[]) => [...rows].sort((a, b) => bandOrder.indexOf(a.size_band) - bandOrder.indexOf(b.size_band));
  const ordered = byBand(bandRows("33"));
  const india = new Map(byBand(bandRows("IN")).map((row) => [row.size_band, row]));
  const W = 720;
  const rowH = 46;
  const left = 96;
  const mid = 396;
  const colW = 240;
  const H = ordered.length * rowH + 66;
  const summary = ordered.map((row) => {
    const tamilNadu = row.unit_share === null
      ? `${row.size_band_label}: Tamil Nadu ${NOT_PUBLISHED}; ${row.suppression_reason ?? "suppressed"}`
      : `${row.size_band_label}: Tamil Nadu establishments ${pct(row.unit_share)}${showJobs ? `, jobs ${pct(row.employment_share!)}` : ""}`;
    const indiaRow = india.get(row.size_band);
    const indiaText = showIndia && indiaRow
      ? indiaRow.unit_share === null
        ? `; India ${NOT_PUBLISHED}`
        : `; India establishments ${pct(indiaRow.unit_share)}${showJobs ? `, jobs ${pct(indiaRow.employment_share!)}` : ""}`
      : "";
    return tamilNadu + indiaText;
  }).join(". ");
  return (
    <figure className="dense-chart" role="img" aria-label={`Unincorporated manufacturing size shares. ${summary}.`}>
      <svg aria-hidden="true" focusable="false" viewBox={`0 0 ${W} ${H}`}>
        <Hatch id="hatch-size" />
        <text x={left} y={18} fontSize="13" fontWeight="600" fill="var(--ink-2)">
          Share of establishments
        </text>
        {showJobs && (
          <text x={mid} y={18} fontSize="13" fontWeight="600" fill="var(--ink-2)">
            Share of jobs
          </text>
        )}
        {ordered.map((row, index) => {
          const y = 40 + index * rowH;
          const suppressed = row.stability === "suppressed";
          const inRow = india.get(row.size_band);
          const tick = (xPos: number) => (
            <line x1={xPos} y1={y - 3} x2={xPos} y2={y + 25} stroke="var(--ink)" strokeWidth="2" />
          );
          /* If the India tick falls where the value label would sit, the
             label shifts right of the tick instead of colliding with it. */
          const labelX = (colStart: number, share: number, tickShare: number | null | undefined) => {
            const base = colStart + Math.max(2, share * colW) + 8;
            if (!showIndia || tickShare == null) return base;
            const tickX = colStart + tickShare * colW;
            return tickX >= base - 12 && tickX <= base + 46 ? tickX + 8 : base;
          };
          return (
            <g key={row.size_band}>
              <text x={left - 10} y={y + 15} textAnchor="end" fontSize="13.5" fill="var(--ink-2)">
                {row.size_band_label}
              </text>
              {suppressed ? (
                <g>
                  <rect x={left} y={y} width={colW} height={22} fill="url(#hatch-size)" />
                  {showJobs && <rect x={mid} y={y} width={colW} height={22} fill="url(#hatch-size)" />}
                  <text
                    x={left + 8}
                    y={y + 15}
                    fontSize="12"
                    fontStyle="italic"
                    fill="var(--ink-3)"
                    stroke="var(--paper)"
                    strokeWidth="3"
                    paintOrder="stroke"
                  >
                    {NOT_PUBLISHED}
                  </text>
                </g>
              ) : (
                <g>
                  {/* Ticks draw first; the value labels carry a paper halo so a
                      nearby India tick passes behind the digits, not through. */}
                  <rect x={left} y={y} width={Math.max(2, row.unit_share! * colW)} height={22} fill="var(--asuse)" />
                  {showIndia && inRow?.unit_share != null && tick(left + inRow.unit_share * colW)}
                  <text x={labelX(left, row.unit_share!, inRow?.unit_share)} y={y + 15} fontSize="13" fill="var(--ink-2)" stroke="var(--paper)" strokeWidth="3" paintOrder="stroke">
                    {pct(row.unit_share!)}
                  </text>
                  {showJobs && (
                    <g>
                      <rect x={mid} y={y} width={Math.max(2, row.employment_share! * colW)} height={22} fill="var(--asuse)" opacity="0.55" />
                      {showIndia && inRow?.employment_share != null && tick(mid + inRow.employment_share * colW)}
                      <text x={labelX(mid, row.employment_share!, inRow?.employment_share)} y={y + 15} fontSize="13" fill="var(--ink-2)" stroke="var(--paper)" strokeWidth="3" paintOrder="stroke">
                        {pct(row.employment_share!)}
                      </text>
                    </g>
                  )}
                </g>
              )}
            </g>
          );
        })}
        {showIndia && (
          <g>
            <line x1={mid + colW - 118} y1={6} x2={mid + colW - 118} y2={20} stroke="var(--ink)" strokeWidth="2" />
            <text x={mid + colW - 110} y={18} fontSize="12" fill="var(--ink-2)">
              = India, same measure
            </text>
          </g>
        )}
        <text x={left} y={H - 8} fontSize="12" fill="var(--ink-3)">
          Each row is a band of workers per establishment · Tamil Nadu, unincorporated manufacturing, ASUSE 2023-24
        </text>
      </svg>
    </figure>
  );
}

// ---------------------------------------------------------------------------
// Exhibit: middle diagnostic across states (Act III)
// ---------------------------------------------------------------------------

const GEO_CODE: Record<string, string> = {
  IN: "India", "24": "GJ", "27": "MH", "29": "KA", "36": "TG", "32": "KL", "33": "TN",
};

function MiddleDiagnostic({ survey, classification }: { survey: string; classification: string }) {
  const geoIds = ["33", ...PEERS];
  const defs = [...new Set(sv.middle_diagnostic.map((row) => row.middle_definition))];
  const W = 720;
  const defH = 104;
  const left = 118;
  const right = 40;
  const H = defs.length * defH + 46;
  const yTop = 62;
  const rows = sv.middle_diagnostic.filter(
    (row) => row.survey === survey && row.classification === classification && geoIds.includes(row.geography_id),
  );
  const max = Math.max(...rows.map((row) => row.employment_share ?? 0)) * 1.15;
  const x = (value: number) => left + (value / max) * (W - left - right);
  const summary = defs.map((definition) => {
    const definitionRows = rows.filter((row) => row.middle_definition === definition);
    const label = definitionRows[0]?.middle_definition_label ?? definition;
    return `${label}: ${definitionRows.map((row) => `${GEO_CODE[row.geography_id] ?? row.geography_label} ${row.employment_share === null ? NOT_PUBLISHED : pct(row.employment_share, 1)}`).join(", ")}`;
  }).join(". ");
  const treatment = survey !== "asi"
    ? "reported establishment workers"
    : classification === "equal_allocation_approximation"
      ? "equal allocation across units"
      : "whole-return sizing";
  return (
    <figure className="dense-chart" role="img" aria-label={`Employment shares in ${survey === "asi" ? "registered ASI units" : "unincorporated ASUSE establishments"} under ${treatment}. ${summary}.`}>
      <svg aria-hidden="true" focusable="false" viewBox={`0 0 ${W} ${H}`}>
        {defs.map((definition, index) => {
          const y = yTop + index * defH;
          const defRows = rows.filter((row) => row.middle_definition === definition);
          const label = defRows[0]?.middle_definition_label ?? definition;
          const tnRow = defRows.find((row) => row.geography_id === "33");
          return (
            <g key={definition}>
              <text x={left - 10} y={y + 20} textAnchor="end" fontSize="13" fontWeight="600" fill="var(--ink-2)">
                {label}
              </text>
              <line className="axis-line" x1={left} y1={y + 16} x2={W - right} y2={y + 16} />
              {(() => {
                const published = defRows
                  .filter((row) => row.employment_share !== null)
                  .sort((a, b) => a.employment_share! - b.employment_share!);
                const peers = published.filter((row) => row.geography_id !== "33");
                /* Peer dots closer than the width of a label share one joined
                   label, so clusters read as a group instead of colliding. */
                const clusters: { xs: number[]; codes: string[] }[] = [];
                for (const row of peers) {
                  const cx = x(row.employment_share!);
                  const code = GEO_CODE[row.geography_id] ?? row.geography_label;
                  const last = clusters[clusters.length - 1];
                  if (last && cx - last.xs[last.xs.length - 1] < 30) {
                    last.xs.push(cx);
                    last.codes.push(code);
                  } else {
                    clusters.push({ xs: [cx], codes: [code] });
                  }
                }
                const tnRowHere = published.find((row) => row.geography_id === "33");
                return (
                  <g>
                    {peers.map((row) => (
                      <circle key={row.geography_id} cx={x(row.employment_share!)} cy={y + 16} r={6} fill="var(--grey-faint)" stroke="var(--grey-fill)" />
                    ))}
                    {clusters.map((cluster) => (
                      <text
                        key={cluster.codes.join("-")}
                        x={(cluster.xs[0] + cluster.xs[cluster.xs.length - 1]) / 2}
                        y={y - 2}
                        textAnchor="middle"
                        fontSize="11.5"
                        fill="var(--grey-text)"
                      >
                        {cluster.codes.join(" · ")}
                      </text>
                    ))}
                    {tnRowHere && (
                      <g>
                        <circle cx={x(tnRowHere.employment_share!)} cy={y + 16} r={8} fill="var(--tn)" />
                        <text x={x(tnRowHere.employment_share!)} y={y + 44} textAnchor="middle" fontSize="11.5" fontWeight={600} fill="var(--tn)">
                          TN {pct(tnRowHere.employment_share!, 0)}
                        </text>
                      </g>
                    )}
                  </g>
                );
              })()}
              {tnRow?.employment_share == null && (
                <text x={left} y={y + 44} fontSize="12" fontStyle="italic" fill="var(--ink-3)">
                  Tamil Nadu: {NOT_PUBLISHED}
                </text>
              )}
            </g>
          );
        })}
        <text x={left} y={H - 8} fontSize="12" fill="var(--ink-3)">
          Share of {survey === "asi" ? "persons engaged" : "workers"} in units inside each “middle” definition · higher = deeper middle
        </text>
      </svg>
    </figure>
  );
}

// ---------------------------------------------------------------------------
// Exhibit: decomposition split (Act IV)
// ---------------------------------------------------------------------------

function GapSplit({ row, stage }: { row: AdjRow; stage: "raw" | "split" }) {
  const W = 720;
  const H = 240;
  const left = 24;
  const right = 24;
  const scaleMax = Math.max(row.common_support_comparator ?? 0, row.common_support_tn ?? 0) * 1.06;
  const x = (value: number) => left + (value / scaleMax) * (W - left - right);
  const tnValue = row.common_support_tn!;
  const compValue = row.common_support_comparator!;
  const mix = -(row.composition_component ?? 0);
  const gap = -(row.common_support_raw_gap ?? 0);
  const within = -(row.within_component ?? 0);
  const mixShare = mix / gap;
  /* Keep centred annotations inside the canvas even when the two dots sit
     close together near the right edge (small raw gaps, e.g. Telangana). */
  const clampX = (value: number) => Math.min(Math.max(value, left + 130), W - 170);
  return (
    <figure role="img" aria-label={`GVA per person engaged on common support: Tamil Nadu ${lakh(tnValue)}, ${row.comparator_label} ${lakh(compValue)}. Broad-industry composition component ${pct(mixShare, 0)} of the gap; within-component ${pct(1 - mixShare, 0)}.`}>
      <svg aria-hidden="true" focusable="false" viewBox={`0 0 ${W} ${H}`}>
        <Hatch id={`hatch-gap-${row.comparator_id}-${stage}`} />
        <text x={left} y={26} fontSize="14" fontWeight="600" fill="var(--tn)">
          Tamil Nadu
        </text>
        <rect x={left} y={36} width={x(tnValue) - left} height={30} fill="var(--tn)" />
        <text x={x(tnValue) + 10} y={56} fontSize="13.5" fontWeight="600" fill="var(--tn)">
          {lakh(tnValue)}
        </text>
        <text x={left} y={106} fontSize="14" fontWeight="600" fill="var(--grey-text)">
          {row.comparator_label}
        </text>
        <rect x={left} y={116} width={x(compValue) - left} height={30} fill={stage === "raw" ? "var(--grey-fill)" : "var(--grey-faint)"} />
        {stage === "split" && (
          <g>
            <rect x={left} y={116} width={x(tnValue) - left} height={30} fill="var(--grey-fill)" />
            <rect x={x(tnValue)} y={116} width={x(tnValue + mix) - x(tnValue)} height={30} fill={`url(#hatch-gap-${row.comparator_id}-${stage})`} stroke="var(--ink-3)" strokeWidth="1" />
            <rect x={x(tnValue + mix)} y={116} width={x(compValue) - x(tnValue + mix)} height={30} fill="var(--tn)" opacity="0.92" />
            <line x1={x(tnValue)} y1={158} x2={x(tnValue + mix)} y2={158} stroke="var(--ink-3)" strokeWidth="1" />
            <text x={clampX((x(tnValue) + x(tnValue + mix)) / 2)} y={176} textAnchor="middle" fontSize="12.5" fill="var(--ink-2)">
              industry mix · {pct(mixShare, 0)}
            </text>
            <line x1={x(tnValue + mix)} y1={196} x2={x(compValue)} y2={196} stroke="var(--tn)" strokeWidth="1.5" />
            <text x={clampX((x(tnValue + mix) + x(compValue)) / 2)} y={214} textAnchor="middle" fontSize="12.5" fontWeight="600" fill="var(--tn)">
              within the same broad industry groups · {pct(within / gap, 0)}
            </text>
          </g>
        )}
        {stage === "raw" && (
          <g>
            <line x1={x(tnValue)} y1={158} x2={x(compValue)} y2={158} stroke="var(--tn)" strokeWidth="1.5" strokeDasharray="4 3" />
            <text x={clampX((x(tnValue) + x(compValue)) / 2)} y={176} textAnchor="middle" fontSize="13" fontWeight="600" fill="var(--tn)">
              the gap: {lakh(gap)} per person, per year
            </text>
          </g>
        )}
        <text x={left} y={H - 6} fontSize="12" fill="var(--ink-3)">
          GVA per person engaged on common ground ({covLabel(row)} of both workforces), ASI 2023-24
        </text>
      </svg>
    </figure>
  );
}

const CELL_SHORT: Record<string, string> = {
  food_beverage_tobacco: "Food, beverages, tobacco",
  textiles_apparel_leather: "Textiles, apparel, leather",
  wood_paper_printing_other_repair: "Wood, paper, other mfg & repair",
  chemicals_petroleum_pharma_rubber: "Petroleum, chemicals, pharma",
  minerals_metals: "Minerals and metals",
  machinery_electrical_electronics: "Machinery, electrical, computers",
  transport_equipment: "Vehicles & transport equipment",
};

function IndustryDumbbells({ row }: { row: AdjRow }) {
  const W = 720;
  const rowH = 52;
  const left = 236;
  const right = 90;
  const cells = [...row.components].sort((a, b) => (b.comparator_cell_rate - b.tn_cell_rate) - (a.comparator_cell_rate - a.tn_cell_rate));
  const H = cells.length * rowH + 92;
  const max = Math.max(...cells.flatMap((cell) => [cell.tn_cell_rate, cell.comparator_cell_rate])) * 1.05;
  const x = (value: number) => left + (value / max) * (W - left - right);
  const summary = cells.map((cell) =>
    `${CELL_SHORT[cell.cell_id] ?? cell.cell_label}: Tamil Nadu ${lakh(cell.tn_cell_rate)}, ${row.comparator_label} ${lakh(cell.comparator_cell_rate)}`,
  ).join(". ");
  return (
    <figure className="dense-chart" role="img" aria-label={`GVA per person engaged by broad industry group. ${summary}.`}>
      <svg aria-hidden="true" focusable="false" viewBox={`0 0 ${W} ${H}`}>
        {cells.map((cell, index) => {
          const y = 30 + index * rowH;
          const behind = cell.tn_cell_rate < cell.comparator_cell_rate;
          return (
            <g key={cell.cell_id}>
              <text x={left - 10} y={y + 4} textAnchor="end" fontSize="12.5" fill="var(--ink-2)">
                {CELL_SHORT[cell.cell_id] ?? cell.cell_label}
              </text>
              <line x1={x(cell.tn_cell_rate)} y1={y} x2={x(cell.comparator_cell_rate)} y2={y} stroke="var(--grey-faint)" strokeWidth="2" />
              <circle cx={x(cell.comparator_cell_rate)} cy={y} r={6} fill="var(--grey-fill)" />
              <circle cx={x(cell.tn_cell_rate)} cy={y} r={7} fill="var(--tn)" />
              <text x={x(Math.max(cell.tn_cell_rate, cell.comparator_cell_rate)) + 12} y={y + 4} fontSize="12" fill={behind ? "var(--tn)" : "var(--check)"}>
                {behind ? `−${lakh(cell.comparator_cell_rate - cell.tn_cell_rate)}` : `+${lakh(cell.tn_cell_rate - cell.comparator_cell_rate)}`}
              </text>
            </g>
          );
        })}
        <circle cx={24} cy={H - 40} r={6} fill="var(--tn)" />
        <text x={36} y={H - 36} fontSize="12" fill="var(--ink-2)">
          Tamil Nadu
        </text>
        <circle cx={134} cy={H - 40} r={6} fill="var(--grey-fill)" />
        <text x={146} y={H - 36} fontSize="12" fill="var(--ink-2)">
          {row.comparator_label}
        </text>
        <text x={24} y={H - 12} fontSize="12" fill="var(--ink-3)">
          GVA per person engaged, by broad industry group, ASI 2023-24
        </text>
      </svg>
    </figure>
  );
}

function ComparatorPanel({ id }: { id: string }) {
  const row = adjIndustry.get(id)!;
  if (row.stability === "suppressed" || row.common_support_raw_gap === null) {
    return (
      <div>
        <p className="suppressed-note" style={{ margin: "1.4rem 0" }}>
          {NOT_PUBLISHED} at the required coverage: {row.suppression_reason} {row.comparator_label}{" "}
          stays in the comparator set — dropping a peer after seeing the results would be
          cherry-picking — but its decomposition is not shown.
        </p>
      </div>
    );
  }
  const gap = -row.common_support_raw_gap;
  const withinShare = -row.within_component! / gap;
  const sizeRow = adjIndustrySize.get(id);
  const smallGap = Math.abs(gap) < 100000;
  return (
    <div>
      {/* For a near-zero raw gap the mix/within split is noise, so the
          exhibit stays at the raw stage and the note says why. */}
      <GapSplit row={row} stage={smallGap ? "raw" : "split"} />
      <p className="chart-note">
        {smallGap
          ? `Against ${row.comparator_label} the raw gap itself is small (${lakh(Math.abs(gap))} per person), so splitting it into mix and within-industry parts would be reading noise; the split and the industry breakdown are deliberately not shown.`
          : `Within the same broad industries, ${pct(withinShare, 0)} of the ${lakh(gap)} gap with ${row.comparator_label} remains.`}{" "}
        {sizeRow && sizeRow.within_component !== null && sizeRow.common_support_raw_gap !== null && !smallGap
          ? `Adjusting for industry and factory size together, ${pct(sizeRow.within_component / sizeRow.common_support_raw_gap, 0)} remains.`
          : ""}
      </p>
      {!smallGap && <IndustryDumbbells row={row} />}
      <Recon
        items={[
          `ASI 2023-24 · ${row.retained_cell_count} of ${row.total_cell_count} broad industry groups on common support`,
          `covers ${pct(row.tn_denominator_coverage, 1)} of TN and ${pct(row.comparator_denominator_coverage, 1)} of ${row.comparator_label} employment`,
          "decomposition identity checked: mix + within = gap, residual 0",
        ]}
      />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Exhibit: labour share, earnings, protections (Act V)
// ---------------------------------------------------------------------------

function LabourShareBars() {
  const W = 720;
  const rowH = 50;
  const left = 128;
  const right = 84;
  const H = labourShareRows.length * rowH + 44;
  const max = Math.max(...labourShareRows.map((row) => row.value)) * 1.1;
  const x = (value: number) => left + (value / max) * (W - left - right);
  return (
    <figure className="dense-chart" role="img" aria-label={`Labour-cost proxy as a share of factory GVA: ${labourShareRows.map((r) => `${r.label} ${pct(r.value, 1)}`).join(", ")}. The proxy includes emoluments, employer provident-fund contributions and workmen/staff welfare.`}>
      <svg aria-hidden="true" focusable="false" viewBox={`0 0 ${W} ${H}`}>
        {labourShareRows.map((row, index) => {
          const isTn = row.id === "33";
          const y = 18 + index * rowH;
          return (
            <g key={row.id}>
              <text x={left - 10} y={y + 17} textAnchor="end" fontSize="14" fontWeight={isTn ? 600 : 400} fill={isTn ? "var(--tn)" : "var(--grey-text)"}>
                {row.label}
              </text>
              <rect x={left} y={y} width={x(row.value) - left} height={26} fill={isTn ? "var(--tn)" : "var(--grey-faint)"} />
              <text x={x(row.value) + 10} y={y + 18} fontSize="13.5" fontWeight={isTn ? 600 : 400} fill={isTn ? "var(--tn)" : "var(--grey-text)"}>
                {pct(row.value, 1)}
              </text>
            </g>
          );
        })}
        <text x={left} y={H - 6} fontSize="12" fill="var(--ink-3)">
          Emoluments, employer PF contributions and staff welfare as a share of GVA, ASI 2023-24
        </text>
      </svg>
    </figure>
  );
}

function CiDotPanel({
  rows,
  format,
  axisNote,
}: {
  rows: PersonRow[];
  format: (value: number) => string;
  axisNote: string;
}) {
  const W = 720;
  const rowH = 46;
  const left = 128;
  const right = 96;
  const published = rows.filter((row) => row.estimate !== null);
  const H = rows.length * rowH + 40;
  const max = Math.max(...published.map((row) => row.ci95_upper ?? row.estimate!)) * 1.06;
  const x = (value: number) => left + (value / max) * (W - left - right);
  const summary = rows.map((row) => {
    if (row.estimate === null) return `${row.geography_label}: ${NOT_PUBLISHED}`;
    const interval = row.ci95_lower !== null && row.ci95_upper !== null
      ? `, 95% confidence interval ${format(row.ci95_lower)} to ${format(row.ci95_upper)}`
      : ", confidence interval unavailable";
    const precision = row.stability === "low_precision" ? ", low precision" : "";
    return `${row.geography_label}: ${format(row.estimate)}${interval}${precision}`;
  }).join(". ");
  return (
    <figure className="dense-chart" role="img" aria-label={`${axisNote}. ${summary}.`}>
      <svg aria-hidden="true" focusable="false" viewBox={`0 0 ${W} ${H}`}>
        {rows.map((row, index) => {
          const isTn = row.geography_id === "33";
          const y = 20 + index * rowH;
          if (row.estimate === null) {
            return (
              <g key={row.geography_id}>
                <text x={left - 10} y={y + 4} textAnchor="end" fontSize="14" fill="var(--grey-text)">
                  {row.geography_label}
                </text>
                <text x={left} y={y + 4} fontSize="12" fontStyle="italic" fill="var(--ink-3)">
                  {NOT_PUBLISHED}
                </text>
              </g>
            );
          }
          const lowPrecision = row.stability === "low_precision";
          return (
            <g key={row.geography_id}>
              <text x={left - 10} y={y + 4} textAnchor="end" fontSize="14" fontWeight={isTn ? 600 : 400} fill={isTn ? "var(--tn)" : "var(--grey-text)"}>
                {row.geography_label}
              </text>
              {row.ci95_lower !== null && row.ci95_upper !== null && (
                <line x1={x(row.ci95_lower)} y1={y} x2={x(row.ci95_upper)} y2={y} stroke={isTn ? "var(--tn)" : "var(--grey-fill)"} strokeWidth="2" opacity="0.55" />
              )}
              <circle cx={x(row.estimate)} cy={y} r={isTn ? 8 : 6} fill={lowPrecision ? "var(--paper)" : isTn ? "var(--tn)" : "var(--grey-fill)"} stroke={isTn ? "var(--tn)" : "var(--grey-fill)"} strokeWidth={lowPrecision ? 2 : 0} />
              <text x={x(row.ci95_upper ?? row.estimate) + 10} y={y + 4} fontSize="12.5" fontWeight={isTn ? 600 : 400} fill={isTn ? "var(--tn)" : "var(--grey-text)"}>
                {format(row.estimate)}
                {lowPrecision ? " (low precision)" : ""}
              </text>
            </g>
          );
        })}
        <text x={left} y={H - 6} fontSize="12" fill="var(--ink-3)">
          {axisNote}
        </text>
      </svg>
    </figure>
  );
}

// ---------------------------------------------------------------------------
// Exhibit: validation ledger (Act VII)
// ---------------------------------------------------------------------------

function ValidationLedger() {
  /* Some checks store a relative error, others (values published to a fixed
     number of decimals) store an absolute one; derive a comparable relative
     figure either way so the column never prints NaN. */
  const relError = (check: ValidationCheck) => {
    if (check.relative_error != null) return check.relative_error;
    if (check.absolute_error != null && check.published !== 0) return Math.abs(check.absolute_error / check.published);
    return null;
  };
  const fmtValue = (value: number) =>
    Math.abs(value) >= 1000 ? int(value) : Number.isInteger(value) ? int(value) : String(Number(value.toPrecision(4)));
  const rseCheck = payload.validation.find((check) => check.check === "ASUSE TN all-activity GVA-per-worker RSE");
  return (
    <div className="table-scroll">
      <table className="ledger-table">
        <caption className="sr-only">Results of the 28 predeclared validation checks</caption>
        <thead>
          <tr>
            <th scope="col">Published figure the build must reproduce</th>
            <th scope="col" className="num">Ours</th>
            <th scope="col" className="num">Published</th>
            <th scope="col" className="num">Status and difference</th>
          </tr>
        </thead>
        <tbody>
          {payload.validation.map((check) => {
            const rel = relError(check);
            return (
              <tr key={check.check}>
                <th scope="row">{check.check}</th>
                <td className="num">{fmtValue(check.reconstructed)}</td>
                <td className="num">{fmtValue(check.published)}</td>
                <td className="num" style={{ color: "var(--check)" }}>
                  Pass · {rel === 0 ? "exact" : rel === null ? "within tolerance" : `${(rel * 100).toFixed(3)}% difference`}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      {rseCheck && (
        <p className="chart-note">
          The one visibly larger difference is deliberate: the RSE row checks our replication of
          MoSPI’s published sampling-error figure (ours {Number(rseCheck.reconstructed.toPrecision(3))} vs{" "}
          {Number(rseCheck.published.toPrecision(3))} published). The official variance machinery
          uses listing data that is not public, so that check carries a wider 15% tolerance —
          the estimate itself has a sampling error of about {Number(rseCheck.published.toPrecision(3))}%,
          which is small.
        </p>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Policy ledger (Act VI) — from the verified Layer 6 evidence base
// ---------------------------------------------------------------------------

const INSTRUMENTS = [
  {
    name: "Scale-up capital subsidy",
    desc: "Pays an extra 5% capital subsidy, up to ₹25 lakh ($30,000), to micro and small units that grow into the next size class.",
    docs:
      "MSME Policy Note 2025-26, p. 37: an additional 5% capital subsidy, capped at ₹25 lakh, for micro units graduating to small or medium and small units graduating to medium. The government reports ₹359.99 crore ($43 million) disbursed to 2,481 enterprises across capital subsidies in 2024-25 (p. 38).",
    source: "MSME Policy Note 2025-26",
    aims: "getting bigger",
    outputKnown: true,
  },
  {
    name: "Payroll (EPF) subsidy",
    desc: "Reimburses employers' provident-fund contributions for three years, once a unit employs more than 20 people.",
    docs:
      "MSME Policy Note 2025-26, p. 38: employer EPF contributions reimbursed for units employing more than 20 persons, for the first three years, up to ₹24,000 ($290) per employee per year. The documents we reviewed publish no series on how many units claim it or what happened to EPF coverage.",
    source: "MSME Policy Note 2025-26",
    aims: "hiring more",
    outputKnown: false,
  },
  {
    name: "Sector missions and parks",
    desc: "Sector-specific policies and industrial-park construction, aimed at attracting investment.",
    docs:
      "Industries Policy Note 2025-26: sector policies and park construction continue under current budget allocations. The documents report investment sanctions and construction outputs — memoranda signed, parks built — not what those investments went on to produce.",
    source: "Industries Policy Note 2025-26",
    aims: "attracting investment",
    outputKnown: true,
  },
  {
    name: "MSME credit",
    desc: "About ₹2.5 lakh crore ($30 billion) of reported lending to micro, small and medium enterprises.",
    docs:
      "The reviewed documents report MSME lending volumes as an aggregate — roughly ₹2.5 lakh crore. They do not report whether that lending made any recipient grow, hire or invest; volume is the last thing measured.",
    source: "MSME Policy Note 2025-26",
    aims: "credit volume",
    outputKnown: true,
  },
];

// ---------------------------------------------------------------------------
// The page
// ---------------------------------------------------------------------------

export default function Home() {
  const singleBand = sv.establishment_size.find(
    (row) => row.survey === "asuse" && row.geography_id === "33" && row.size_band === "1" && row.classification === "reported_establishment_workers",
  )!;
  const employerShare = payload.headline.hired_worker_share;
  const gjGap = -gj.common_support_raw_gap!;
  const gjMixShare = -gj.composition_component! / gjGap;
  const tgRaw = adjIndustry.get("36")!;
  const emolAdj = sv.peer_comparisons_adjusted.find(
    (row) => row.survey === "asi" && row.outcome === "emoluments_per_paid_person_engaged" && row.adjustment_dimension === "industry" && row.comparator_id === "36",
  );
  const contractKa = sv.worker_job_quality.find((row) => row.concept === "written_contract" && row.dimension === "overall" && row.geography_id === "29")!;
  const contractTg = sv.worker_job_quality.find((row) => row.concept === "written_contract" && row.dimension === "overall" && row.geography_id === "36")!;

  const SECTIONS = [
    { id: "paradox", label: "The paradox" },
    { id: "surveys", label: "How India counts" },
    { id: "middle", label: "Not the missing middle" },
    { id: "fair-test", label: "Within-industry comparison" },
    { id: "workers", label: "The workers’ slice" },
    { id: "policy", label: "What policy aims at" },
    { id: "methods", label: "Limits and the ledger" },
  ];

  return (
    <main>
      <SectionNav sections={SECTIONS} />
      {/* ---------------- Act I — the paradox ---------------- */}
      <header className="hero">
        <div className="hero-inner">
          <h1>
            <CountUp value={panel.tnPersons} className="hero-count" />
            <span className="hero-title">
              people work in Tamil Nadu’s registered factories — more than in any other state
              in India.
            </span>
          </h1>
          <p className="hero-sub">
            {perHundred}{" "}of every 100 Indian factory workers work there. Yet Tamil Nadu’s
            factories add less value per person than those in India overall and in each of the
            five other manufacturing states this page compares it with. This page measures that
            gap, tests the explanations this data can test, and reads the state’s own policy
            documents alongside it.
          </p>
          <p className="hero-source">
            Computed from Annual Survey of Industries 2023-24 factory returns
            {tnIsFirst ? "; the same panel puts Tamil Nadu first" : ""} · totals match the
            official Statement 7A release within 0.25% · rank confirmed by Tamil Nadu Economic
            Survey Table 4.1
          </p>
          <p className="hero-scrollcue" aria-hidden="true">
            Keep scrolling ↓
          </p>
        </div>
      </header>

      {/* ---------------- The finding, up front ---------------- */}
      <section className="bluf" aria-label="The finding in brief">
        <div className="column">
          <p className="bluf-kicker">The finding, up front</p>
          <p>
            India’s largest registered-factory workforce produces the least value per person of
            the areas this page compares it with. One popular explanation — that Tamil Nadu
            lacks mid-sized factories, the “missing middle” — does not hold in the
            registered-factory data: under four different definitions of “mid-sized” (10–249,
            10–99, 20–249 and 50–249 workers), Tamil Nadu’s middle is not unusually small. A
            second explanation — that Tamil Nadu simply has different industries — accounts for
            only part of the gap: re-run the comparison as if both sides had the same broad
            industry mix, and most of the gap against Gujarat, Maharashtra and Karnataka
            remains. Meanwhile, spending on labour takes a larger share of factory value in
            Tamil Nadu than in any comparison area, even though the pay workers themselves
            report is middling. And the state programmes in the policy documents we reviewed
            support investment, growing into a bigger size category, hiring, and credit — but
            none of those documents measures whether any of the programmes works.
          </p>
          <p>The rest of this page is the evidence for each of those sentences, in order.</p>
          <nav className="route" aria-label="Jump to a section">
            {SECTIONS.map((section, index) => (
              <a key={section.id} href={`#${section.id}`}>
                <span className="n">{index + 1}</span>
                {section.label}
              </a>
            ))}
          </nav>
        </div>
      </section>

      <section className="act" id="paradox" aria-label="The paradox">
        <Scrolly
          ariaLabel="Comparing selected geographies by GVA per person engaged"
          steps={[
            <div key="s0">
              <p>
                Being India’s factory-jobs state is an old distinction; Tamil Nadu has held
                it for years. But line the same places up by a different measure: the value
                each factory adds for every person engaged in it.
              </p>
              <p className="definition">
                The surveys call that measure <strong>gross value added (GVA) per person
                engaged</strong> — the value of what a factory ships out, minus the materials
                and services it buys in, divided by everyone engaged in the factory, owners and
                unpaid family members included. It describes the factory, not the effort or
                skill of any individual worker.
              </p>
              <p>Tamil Nadu comes last among the areas shown.</p>
            </div>,
            <div key="s1">
              <p>
                About {lakhUsd(gvaPerPerson("33"))} of value added per person per year — against{" "}
                {lakhUsd(gvaPerPerson("24"))} in Gujarat and {lakhUsd(gvaPerPerson("27"))} in
                Maharashtra. Among the six comparators only Telangana is close.
              </p>
              <p>
                Everything on this page is computed from Government of India surveys of
                2023-24 and shown with its limits. Where direct official counterparts exist,
                the specified validation checks are reported separately. Dollar figures use ₹{USD_RATE} to the US dollar,
                roughly the 2023-24 average.
              </p>
            </div>,
          ]}
          states={[<RankStrip key="plain" annotated={false} />, <RankStrip key="annotated" annotated />]}
        />
        <div className="column">
          <p className="handoff">
            Where does the gap come from? Start with how India counts its manufacturing. No
            single survey can see all of it.
          </p>
        </div>
      </section>

      {/* ---------------- Act II — three lenses ---------------- */}
      <section className="act" id="surveys" aria-label="Three surveys">
        <hr className="act-rule" />
        <div className="column">
          <h2 className="act-title">Three surveys, three worlds</h2>
          <p>
            India measures manufacturing with three separate government surveys. They knock on
            different doors, ask different questions, and cannot be stitched together. Every
            chart on this page names which survey it draws on.
          </p>
        </div>
        <div className="exhibit-column">
          <div className="table-scroll">
            <table className="ledger-table" style={{ marginTop: "2rem" }}>
              <caption>The three surveys and what each one can see</caption>
              <thead>
                <tr>
                  <th>Survey</th>
                  <th>Who it visits</th>
                  <th>In Tamil Nadu’s manufacturing</th>
                  <th>What it cannot see</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <span className="survey-tag asuse">ASUSE</span>
                    <br />
                    <span className="suppressed-note" style={{ fontStyle: "normal" }}>Annual Survey of Unincorporated Sector Enterprises</span>
                  </td>
                  <td>
                    Unincorporated establishments — the tailor’s shop, the grinding mill,
                    the ten-person workshop
                  </td>
                  <td className="evidence">{int(payload.headline.unincorporated_establishments)} establishments</td>
                  <td>Registered factories; anything incorporated</td>
                </tr>
                <tr>
                  <td>
                    <span className="survey-tag asi">ASI</span>
                    <br />
                    <span className="suppressed-note" style={{ fontStyle: "normal" }}>Annual Survey of Industries</span>
                  </td>
                  <td>Registered factories, through their annual returns</td>
                  <td className="evidence">{int(payload.headline.registered_factories)} factories</td>
                  <td>The unregistered workshop economy</td>
                </tr>
                <tr>
                  <td>
                    <span className="survey-tag plfs">PLFS</span>
                    <br />
                    <span className="suppressed-note" style={{ fontStyle: "normal" }}>Periodic Labour Force Survey</span>
                  </td>
                  <td>Workers themselves, at home, about their jobs</td>
                  <td className="evidence">
                    {payload.plfs.manufacturing_share.toFixed(1)}% of workers ({int(payload.plfs.sample_workers)} sampled)
                  </td>
                  <td>The establishment’s books; output and value</td>
                </tr>
              </tbody>
            </table>
          </div>
          <Recon
            items={[
              "ASUSE establishment count matches the published state total to 0.003%",
              "ASI factory count within 0.25% of Statement 7A",
              "PLFS manufacturing share reproduces published Table 27",
            ]}
          />
        </div>
        <div className="column" style={{ marginTop: "1.8rem" }}>
          <p>
            No common identifier links the three surveys’ records, and their universes
            overlap only partially, so they cannot be merged into one ladder from workshop to
            factory. The same workshop is never observed becoming a factory in this data. When a
            chart on this page switches from one survey to another, its label says so.
          </p>
          <p className="handoff">
            Start with the workshops and factories themselves: is Tamil Nadu’s problem that
            its firms never grow to the middle?
          </p>
        </div>
      </section>

      {/* ---------------- Act III — missing middle ---------------- */}
      <section className="act" id="middle" aria-label="Testing the missing middle">
        <hr className="act-rule" />
        <div className="column">
          <h2 className="act-title">Testing the missing middle</h2>
          <p>
            For decades, economists’ leading diagnosis of Indian manufacturing has been
            the <strong>missing middle</strong>: plenty of tiny units, a few giants, and
            abnormally few mid-size firms in between (
            <a href="https://icrier.org/pdf/Workingpaper230.pdf">Krueger 2009</a>;{" "}
            <a href="https://www.routledge.com/Globalization-Labour-Markets-and-Inequality-in-India/Mazumdar-Sarkar/p/book/9781003060956">
              Mazumdar and Sarkar 2008
            </a>
            ). If that were Tamil Nadu’s disease, the fix would be obvious — and the state
            already runs a subsidy aimed at exactly that. The diagnosis is also contested (
            <a href="https://www.aeaweb.org/articles?id=10.1257/jep.28.3.89">Hsieh and Olken 2014</a>
            ), which is one more reason to check it against the data before building a story on
            it.
          </p>
        </div>
        <Scrolly
          ariaLabel="Size structure and the middle diagnostic"
          steps={[
            <div key="s0">
              <p>
                Count <strong>establishments</strong>, and Tamil Nadu’s workshop economy is
                overwhelmingly tiny: {pct(singleBand.unit_share!, 0)} of its{" "}
                {int(payload.headline.unincorporated_establishments)} unincorporated manufacturing
                establishments — the workshops outside the registered factory system — are one
                person working alone.
              </p>
              <p className="definition">
                Each row of the chart is a size of establishment, measured in workers; each bar
                is that size’s share of all establishments.
              </p>
            </div>,
            <div key="s1">
              <p>
                Count <strong>jobs</strong> instead and the picture spreads out: single-person
                units hold {pct(singleBand.employment_share!, 0)}{" "}of the workshop economy’s
                jobs, and units of five or more hold most of the rest.
              </p>
              <p>
                The black ticks are India on the same measures. Across India, single-person units
                are an even larger share of establishments than in Tamil Nadu — tiny workshops
                dominating the count is normal, not a Tamil Nadu disease.
              </p>
            </div>,
            <div key="s2">
              <p>
                The real question is comparative: does Tamil Nadu have an <em>abnormally thin</em>{" "}
                middle? We tested four definitions of “the middle” — from 10–99
                workers to 50–249 — across Tamil Nadu, five peer states and India.
              </p>
              <p className="definition">
                Note the survey switch: the chart now shows registered factories (ASI), where
                mid-size units are well sampled and publishable. The workshop survey above could
                not publish its 50-plus bands for exactly the opposite reason — almost nothing
                unincorporated is that big.
              </p>
            </div>,
            <div key="s3">
              <p>
                Within registered factories, Tamil Nadu’s middle is not unusually small next to
                the peers shown, under any of the four definitions. The result also holds under
                both ways of sizing a factory (below). What it does not show: how often a small
                workshop grows into a factory — these surveys photograph a single year and
                cannot follow a firm over time.
              </p>
            </div>,
          ]}
          stepToState={[0, 1, 2, 2]}
          states={[
            <SizeBars key="places" showJobs={false} />,
            <SizeBars key="jobs" showJobs showIndia />,
            <MiddleDiagnostic key="diag" survey="asi" classification="equal_allocation_approximation" />,
          ]}
        />
        <div className="exhibit-column">
          <Exhibit
            title="The verdict survives both ways of sizing a factory"
            sub="One ASI paper return can cover several factories under the same owner, so 'how big is this factory' needs a rule. Split the return's workers evenly across its units, or keep each return whole (official practice) — the middle looks the same either way."
          >
            <Tabs
              ariaLabel="Classification sensitivity"
              labels={["Split evenly across units", "Whole returns (official practice)"]}
              panels={[
                <MiddleDiagnostic key="ea" survey="asi" classification="equal_allocation_approximation" />,
                <MiddleDiagnostic key="pr" survey="asi" classification="per_return_sensitivity" />,
              ]}
            />
            <Recon
              items={[
                "whole-return sizing reproduces official Statement 14A (the published ASI table of factories by employment size) to 0.01 percentage points",
                "the same diagnostic cannot be run on unincorporated workshops: every Tamil Nadu middle band there is " + NOT_PUBLISHED + ", as it is for most states",
              ]}
            />
          </Exhibit>
        </div>
        <div className="column">
          <p>
            One more thing the workshop data says: Tamil Nadu’s unincorporated sector is
            unusually likely to be an employer at all — {pct(employerShare, 0)}{" "}of its
            establishments have at least one hired worker, far above the national average. And its
            workshops’ value added per worker{tnAsuseGva ? ` (${rupeesUsd(tnAsuseGva)} a year)` : ""} stands{" "}
            <em>above</em> India’s, Karnataka’s and Telangana’s. Whatever is
            dragging on Tamil Nadu’s factories, its workshop economy looks comparatively
            healthy.
          </p>
          <HowWeKnow>
            <p>
              <strong>Estimand.</strong> Establishment and employment shares by workers-per-establishment band
              (ASUSE: reported workers; ASI: persons engaged). ASI returns may cover multiple units:
              the primary series divides return employment equally across reported units
              (“equal-allocation approximation”), the sensitivity series sizes whole
              returns, matching official practice — the per-return series reproduces official
              Statement 14A: Tamil Nadu’s 100+ unit share 28.42% vs 28.43% published, and
              Economic Survey Table 4.11’s 100+ employment shares to 0.1–0.3 points.
              The equal-allocation treatment moves Tamil Nadu’s large-factory employment
              share by about 4 points; both are shown wherever size matters.
            </p>
            <p>
              <strong>Suppression.</strong> Cells resting on fewer than 10 sampled units, or where
              one unit carries more than 70% of the weighted total, are {NOT_PUBLISHED} — rendered
              hatched, never as zero. The Tamil Nadu Economic Survey publishes ASUSE medium/large
              cells that rest on ≤9 sampled establishments; this project deliberately does not.
            </p>
            <p>
              <strong>Uncertainty.</strong> MoSPI’s published ASUSE relative standard errors
              (Tables 46–49) are the uncertainty context for establishment-side estimates; a
              full replication of those RSEs from the public-use files was attempted and is
              documented as infeasible (the official variance uses listing-schedule data that is
              not public). ASI publishes no state-level RSEs.
            </p>
            <p>
              <strong>Sources.</strong> ASUSE 2023-24 unit records (public use); ASI 2023-24
              Statement 14A; TN Economic Survey 2025-26 Tables 4.7, 4.10, 4.11.
            </p>
          </HowWeKnow>
          <p className="handoff">
            So the registered-factory data do not show a uniquely missing middle. Next
            hypothesis: maybe Tamil Nadu simply has different industries.
          </p>
        </div>
      </section>

      {/* ---------------- Act IV — the fair test ---------------- */}
      <section className="act" id="fair-test" aria-label="Industry mix and the fair test">
        <hr className="act-rule" />
        <div className="column">
          <h2 className="act-title">The fair test</h2>
          <p>
            Tamil Nadu and Gujarat spread their factory jobs across very different industries.
            An overall average therefore mixes two things: <em>which</em> industries each state
            has, and how much value is added <em>within</em> each industry. The question tested
            here is:{" "}
            <strong>how much of the gap is accounted for by the industry mix alone?</strong>
          </p>
          <p className="definition">
            So we re-run each comparison as if both states had the same industry mix. The
            standard statistical tool for this is a <strong>Kitagawa decomposition</strong>: it
            splits an observed gap into the part that reflects the two states having different
            industries (the <strong>composition component</strong>) and the part that remains
            inside the same broad industry groups (the <strong>within component</strong>). One
            honest limit up front: it works at seven broad industry groups, so it does not
            control products, capital, technology, management, prices or markups — differences
            inside a broad group stay in the “within” part.
          </p>
        </div>
        <Scrolly
          ariaLabel="Decomposing the gap with Gujarat"
          steps={[
            <div key="s0">
              <p>
                Take Gujarat. On common ground — the broad industries both states actually
                have, which cover{" "}
                {covLabel(gj)} of the two states’ factory workforces — Gujarat records{" "}
                {lakh(gjGap)} more GVA per person engaged than Tamil Nadu.
              </p>
            </div>,
            <div key="s1">
              <p>
                Give both states the same industry mix, and {pct(gjMixShare, 0)} of that gap is
                accounted for — that part reflects which industries each state has.
              </p>
              <p>
                The remaining {pct(1 - gjMixShare, 0)} survives: even inside the same broad
                industry groups, Tamil Nadu’s factories add less value per person than
                Gujarat’s. The data show that this is so, not why.
              </p>
            </div>,
            <div key="s2">
              <p>
                And it is not one rogue industry: Tamil Nadu’s value added per person trails
                Gujarat’s across most of the board, garments and machinery and chemicals
                alike.
              </p>
            </div>,
          ]}
          states={[
            <GapSplit key="raw" row={gj} stage="raw" />,
            <GapSplit key="split" row={gj} stage="split" />,
            <IndustryDumbbells key="cells" row={gj} />,
          ]}
        />
        <div className="exhibit-column">
          <Exhibit
            title="The within-industry gap holds against every major comparator"
            sub="The comparators: India, the two states just behind Tamil Nadu on factory employment (Gujarat and Maharashtra, themselves the top two on total value added), and the three southern neighbours. One comparator at a time — each comparison uses its own common ground, so the panels must not be read as a ranked table."
          >
            <Tabs
              ariaLabel="Comparator"
              labels={["India", "Gujarat", "Maharashtra", "Karnataka", "Telangana", "Kerala"]}
              defaultIndex={1}
              panels={[
                <ComparatorPanel key="IN" id="IN" />,
                <ComparatorPanel key="24" id="24" />,
                <ComparatorPanel key="27" id="27" />,
                <ComparatorPanel key="29" id="29" />,
                <ComparatorPanel key="36" id="36" />,
                <ComparatorPanel key="32" id="32" />,
              ]}
            />
          </Exhibit>
        </div>
        <div className="column">
          <p>
            Across India, Gujarat, Maharashtra and Karnataka, industry mix explains between a
            seventh and a half of the gap, depending on how finely you slice the industries. The
            within-industry component is the <strong>majority of the gap in every specification
            we tested</strong>: seven broad groups, twenty-four detailed industries, and
            industry-by-size jointly. And Tamil Nadu’s factory value added per person has
            sat below Gujarat’s, Maharashtra’s and Karnataka’s{" "}
            {panel.alwaysBelow ? "in every single year we can compute, 2008-09 through 2023-24" : "for most of the last decade and a half"}.
            That persistence rules out a single unusual year as the explanation, and the
            industry mix accounts for only part of the gap.
          </p>
          <p>
            Two comparators behave differently, and the page says so. Against Telangana the raw
            gap is small
            {tgRaw.common_support_raw_gap !== null ? ` (${lakh(Math.abs(tgRaw.common_support_raw_gap))} per person)` : ""}, so
            there is little to decompose
            {emolAdj && emolAdj.composition_component !== null && emolAdj.common_support_raw_gap !== null
              ? `; and while Tamil Nadu's factories record higher pay per paid person than Telangana's on the raw average, ${pct(
                  emolAdj.composition_component / emolAdj.common_support_raw_gap,
                  0,
                )} of that pay gap reflects which broad industries each state has, not pay differences inside the same broad groups`
              : ""}
            . Against Kerala the decomposition does not reach the required 95% coverage of both
            workforces, so it is {NOT_PUBLISHED}; Kerala stays in the comparator set because
            dropping a peer after seeing the results would be cherry-picking.
          </p>
          <p>
            What could still differ inside these broad groups? This standardisation does not
            control products, capital, technology, management, prices or markups. The panel
            separately describes <strong>fixed capital</strong>: Tamil Nadu’s factories
            work with roughly a third of Gujarat’s fixed capital per person, and about half of
            Maharashtra’s and Karnataka’s. That pattern is not uniform. In electrical and
            electronics manufacture, Tamil Nadu holds{" "}
            {panel.elec.capitalMin.toFixed(1)}–{panel.elec.capitalMax.toFixed(1)} times the
            fixed capital per person of Gujarat, Maharashtra and Karnataka — and still
            produces {pct(panel.elec.shortfallMin, 0)}–{pct(panel.elec.shortfallMax, 0)} less
            value per person than each of them. Across the observed panel, the descriptive gap is
            broad across industries and persists over sixteen complete years. These data do not
            identify its causes.
          </p>
          <HowWeKnow>
            <p>
              <strong>Method.</strong> Pairwise symmetric Kitagawa standardisation on ASI 2023-24:
              rates are GVA per person engaged in seven broad industry groups; the counterfactual
              weights each group by the average of the two states’ employment shares.
              Identities hold exactly in the published data: composition + within = common-support
              gap, residual zero. Rows are published only when the retained groups cover at least
              95% of both states’ denominators; the Tamil Nadu–Kerala row fails that
              gate and is suppressed.
            </p>
            <p>
              <strong>Wording discipline.</strong> “Adjusted” means the gap remaining
              under a common industry mix — a descriptive standardisation, not a causal estimate.
              No confidence intervals are published for decomposition rows: the surveys’
              public files do not support design-based variances for these functionals, and we do
              not print intervals we cannot defend.
            </p>
            <p>
              <strong>Robustness (2026-07-14 battery).</strong> Re-run at 24 NIC 2-digit
              industries with employment weights recomputed from the raw returns, the
              within-industry share of the gap is 54–86% against India, Gujarat, Maharashtra
              and Karnataka (7 groups: 67–84%; industry×size jointly: 56–81%). Tamil
              Nadu’s rate sits below the comparator’s in 16–22 of ~23 published
              industry cells covering 74–97% of common-weight employment. Panel persistence
              and capital-intensity descriptives come from the committed ASI aggregates
              (research/derived), reproduced in research/docs/ROBUSTNESS_WITHIN_INDUSTRY.md.
            </p>
            <p>
              <strong>Sources.</strong> ASI 2023-24 unit returns; classification map in the
              methods repository (LAYER5_FIELD_MAP.md); external checks in EXTERNAL_VALIDATION.md.
            </p>
          </HowWeKnow>
          <p className="handoff">
            So a substantial gap remains even when both states are given the same industry mix.
            Next question: how is the value factories add divided up?
          </p>
        </div>
      </section>

      {/* ---------------- Act V — the workers' slice ---------------- */}
      <section className="act" id="workers" aria-label="Pay, protections and the labour share">
        <hr className="act-rule" />
        <div className="column">
          <h2 className="act-title">The workers’ slice</h2>
          <p>
            Of the value its factories add, Tamil Nadu spends a larger share on labour than any
            comparison area shown. “Labour cost” here is the survey’s broad measure — pay plus
            the employer’s provident-fund contributions and staff-welfare spending — so it is
            wider than what workers take home.
          </p>
        </div>
        <div className="exhibit-column">
          <Exhibit
            title={`Labour's share of factory value added is ${pp(labourShareRows[0].value - labourShareRows[1].value)} to ${pp(labourShareRows[0].value - labourShareRows[labourShareRows.length - 1].value)} points higher in Tamil Nadu than in every comparator`}
            sub="The labour-cost proxy is emoluments plus employer provident-fund contributions and workmen/staff welfare. Welfare is not necessarily cash pay, so this is broader than workers' earnings or take-home pay."
          >
            <LabourShareBars />
            <Recon
              items={[
                "direction corroborated by MoSPI's own published totals (our narrow emoluments/GVA measure: TN 37.6% vs official 37.4%) and by the TN Economic Survey's ranking",
                "the Economic Survey's own levels (§4.3) could not be reconciled to official ASI totals under any definition tested; its levels are therefore never cited here",
              ]}
            />
          </Exhibit>
        </div>
        <div className="column">
          <p>
            A larger share of a smaller pie can still be a modest amount — and the labour-cost
            measure above comes from factory accounts, not from workers’ pockets. A separate
            survey (the PLFS) asks workers themselves what they earn. Their answers put Tamil
            Nadu’s regular monthly factory pay close to the India-wide figure, with
            self-employment and casual daily work each telling a different story:
          </p>
        </div>
        <div className="exhibit-column">
          <Exhibit
            title="Factory-state pay is middling: near India's average, above Gujarat, below Maharashtra and the southern peers"
            sub="Workers' own reports, manufacturing, 2023-24. Three kinds of work are three different measures — kept separate. Whiskers are 95% confidence intervals from the survey design."
          >
            <Tabs
              ariaLabel="Earnings concept"
              labels={earningsConcepts.map((concept) => concept.label)}
              panels={earningsConcepts.map((concept) => (
                <CiDotPanel
                  key={concept.id}
                  rows={overallPersonRows(sv.worker_earnings, concept.id)}
                  format={(value) => rupees(value)}
                  axisNote={`${concept.label}, ${concept.unit} · recall: ${concept.recall}`}
                />
              ))}
            />
            <Recon
              items={[
                "PLFS 2023-24, first-visit records; intervals from the survey's two-subsample design",
                "the same machinery reproduces the published all-industry rural TN quarterly figure to the rupee",
                `TN regular manufacturing earnings ${rupees(tnEarn.estimate!)}/month (95% CI ${rupees(tnEarn.ci95_lower!)}–${rupees(tnEarn.ci95_upper!)}, n = ${int(tnEarn.sample_count)})`,
              ]}
            />
          </Exhibit>
          <Exhibit
            title={`Half of Tamil Nadu's regular salaried manufacturing workers have a written contract — above India, 14 to 19 points below Karnataka or Telangana`}
            sub="Regular salaried manufacturing workers, usual status. Each measure is the share of workers answering yes; whiskers are 95% confidence intervals."
          >
            <Tabs
              ariaLabel="Job quality measure"
              labels={jobConcepts.map((concept) => concept.label)}
              panels={jobConcepts.map((concept) => (
                <CiDotPanel
                  key={concept.id}
                  rows={overallPersonRows(sv.worker_job_quality, concept.id)}
                  format={(value) => pct(value, 1)}
                  axisNote={concept.label}
                />
              ))}
            />
            <Recon
              items={[
                `TN: written contract ${pct(tnJob("written_contract").estimate!)}, paid leave ${pct(tnJob("paid_leave").estimate!)}, specified social security ${pct(tnJob("specified_social_security").estimate!)}`,
                `Karnataka ${pct(contractKa.estimate!)} and Telangana ${pct(contractTg.estimate!)} on written contracts`,
                "reproduces published PLFS Table 36 no-written-contract shares",
              ]}
            />
          </Exhibit>
        </div>
        <div className="column">
          <p>
            Put together, the worker picture is mixed rather than a single verdict. Labour
            costs take a larger share of factory value than in any comparison area; the pay
            workers report is middling; written contracts, paid leave and social-security
            coverage beat India, Gujarat and Kerala but trail Karnataka and Telangana by double
            digits. These are descriptions of one year, 2023-24. They do not show that workers
            are exploited, that they are not, or that any single lever would raise wages.
          </p>
          <HowWeKnow>
            <p>
              <strong>Labour share.</strong> ASI 2023-24; numerator is the labour-cost proxy
              (emoluments + employer provident-fund contributions + workmen/staff welfare — welfare is not necessarily cash pay), denominator is
              factory GVA, both from the same returns. The narrow emoluments-only share (TN 37.6%)
              reconciles with the share implied by MoSPI’s own published totals (37.4%). The
              TN Economic Survey §4.3 reports much lower levels on an unspecified base that could
              not be reconciled to official ASI totals under any definition we tested — a
              difference in concept or deflation that the Survey does not specify — so its levels
              are not used, while its <em>ranking</em> (TN highest among peers) agrees with ours.
            </p>
            <p>
              <strong>Earnings and protections.</strong> PLFS 2023-24, current-weekly-status
              filter for earnings, principal-activity for job quality; standard errors from the
              two-interpenetrating-subsample design; estimates suppressed below 30 respondents, 10
              active first-stage units, effective n of 30, or where one weight exceeds 20% of the
              cell — suppressed cells read {NOT_PUBLISHED}.
            </p>
          </HowWeKnow>
          <p className="handoff">So what does the state’s own policy say about value, pay and protection?</p>
        </div>
      </section>

      {/* ---------------- Act VI — instruments and the mismatch ---------------- */}
      <section className="act" id="policy" aria-label="Policy instruments">
        <hr className="act-rule" />
        <div className="column">
          <h2 className="act-title">What the state’s policy aims at</h2>
          <p>
            Last, the policy ledger: what support programmes for manufacturers appear in the
            state documents we reviewed? Four kinds: extra capital subsidy for firms that grow
            into a larger official size category, reimbursement of the employer’s
            provident-fund contribution for units employing more than 20 people, investment and
            sector-development programmes, and credit for small enterprises. For each, the
            cards below give the documented design, the documents’ own reported figures and how
            far the published evidence goes.
          </p>
        </div>
        <div className="instrument-grid">
          {INSTRUMENTS.map((instrument) => (
            <article key={instrument.name} className="instrument">
              <h3>{instrument.name}</h3>
              <p className="desc">{instrument.desc}</p>
              <p className="ladder" aria-label="Evidence ladder">
                <span className="on">objective stated</span>
                <span className="on">instrument verified</span>
                <span className={instrument.outputKnown ? "on" : "off"}>
                  output reported{instrument.outputKnown ? "" : ": none found in the documents reviewed"}
                </span>
                <span className="off">outcome measured: no</span>
                <span className="off">impact known: no</span>
              </p>
              <details>
                <summary>What the documents report</summary>
                <p>{instrument.docs}</p>
              </details>
              <p className="source-line">{instrument.source}</p>
            </article>
          ))}
        </div>
        <div className="column" style={{ marginTop: "2rem" }}>
          <p>
            Set those programmes beside the measurements. Their stated designs support
            investing, growing into a larger size category, hiring, and borrowing. In the
            documents we reviewed, we did not find value added per person, wage levels, or
            contract and benefit coverage stated as objectives. That is a finding about these
            documents only — policy runs wider than what is published, and other targets may
            exist in places we could not see. Timing matters too: the state’s general
            Industrial Policy of 2021 expired on 31 March 2025. No enacted or notified
            successor was found as of July 2026; a new policy has been announced but not
            published. The MSME programmes above are as stated in the 2025-26 Policy Notes.
          </p>
          <p className="definition">
            To be precise about what this section claims: it reads stated objectives in
            published documents, nothing more. It passes no verdict on whether any programme
            works, because policy documents record what programmes aim at, disburse and build,
            never what they cause. The observation is simply that the measured gaps sit in one
            place and the stated objectives in another — a question about emphasis, not an
            accusation of neglect. The reading is ours; the documents themselves draw no such
            comparison.
          </p>
          <HowWeKnow>
            <p>
              <strong>Bounded evidence base.</strong> The document search covered the MSME Policy Note 2025-26 (subsidy design pp. 37-38,
              disbursements p. 38), Industries Policy Note 2025-26, TN Economic Survey 2025-26,
              Industrial Policy 2021 (expired 31.03.2025). Every instrument claim carries a
              printed-page citation in the research repository’s Layer 6 ledger; expired
              targets are shown as historical, announced intentions as announcements. The evidence
              ladder stops at “output reported” for every instrument: no reviewed
              document measures take-up against a counterfactual, so nothing here identifies
              causes or evaluates any policy.
            </p>
          </HowWeKnow>
        </div>
      </section>

      {/* ---------------- Act VII — what we can't tell you ---------------- */}
      <section className="act" id="methods" aria-label="Limits and methods">
        <hr className="act-rule" />
        <div className="column">
          <h2 className="act-title">What this page cannot tell you</h2>
          <p>
            Every number here is a snapshot of one year, and a snapshot cannot show movement.
            This data cannot see firms that tried to grow and failed, cannot link a
            worker’s answers to their factory’s books, and cannot evaluate a single
            subsidy. Where the page says “is associated with,” that is the whole
            claim.
          </p>
          <p>
            One caution from the exploratory appendix: when workshop owners are asked what
            problems they face, barely {pct(maxProblemShare, 0)} report any single one — and the
            establishments that <em>do</em> report problems are the bigger, more formal ones.
            Treat that as a warning against tidy constraint stories, not as evidence about
            constraints themselves.
          </p>
        </div>
        <div className="column">
          <Exhibit
            title="Where our numbers have a direct official counterpart, they usually match within 2% — the exceptions are disclosed"
            sub="We ran 28 pre-declared checks against the government's own published tables; all pass their stated tolerances. Not every number on this page has a published counterpart to check against, so this ledger does not mean every number was independently verified."
          >
            <details className="howweknow" style={{ borderTop: "none" }}>
              <summary>Open the full 28-gate reconciliation ledger</summary>
              <div className="howweknow-body">
                <ValidationLedger />
              </div>
            </details>
            <Recon
              items={[
                "beyond the built-in gates: ASUSE state GVA/worker matches published Table 36 within 1.7% across all seven geographies",
                "ASI totals within 0.03-0.25% of Statement 7A / ES Table 4.7",
                "PLFS machinery reproduces one published cell exactly, to the rupee",
              ]}
              flag="one disclosed exception: Karnataka's published ASUSE emoluments figure differs by 3.47% from the project estimate; both values are shown in the research appendix"
            />
          </Exhibit>
        </div>
        <div className="column">
          <HowWeKnow>
            <p>
              <strong>What this page is.</strong> A descriptive account. Nothing on it identifies
              causes or evaluates any policy; every comparison is an association between weighted
              survey aggregates from 2023-24. {payload.meta.price_basis} {payload.meta.comparison_warning}
            </p>
            <p>
              <strong>Disclosure.</strong> {payload.meta.disclosure} Cells resting on fewer than 10
              sampled units, or dominated by one unit, or (PLFS) below effective-sample and weight
              thresholds are {NOT_PUBLISHED} — and are rendered as visible hatched slots, never as
              zero, and never reconstructable from published components.
            </p>
            <p>
              <strong>Uncertainty.</strong> PLFS estimates carry design-based 95% intervals.
              ASUSE/ASI establishment-side estimates carry no project-computed intervals: MoSPI’s
              published ASUSE RSE tables are the uncertainty context (our replication attempt from
              public files is documented as infeasible), and ASI publishes no state RSEs. We print
              no interval we cannot defend.
            </p>
            <p>
              <strong>Reproducibility.</strong> The full pipeline — raw public-use files in,
              canonical payload out, 28 gates enforced in tests — with every method document and
              the external-validation register is public in the{" "}
              <a href="https://github.com/smar98/tamil-nadu-manufacturing-structure">research repository</a>.
              Raw unit records stay local per MoSPI terms; only aggregates are published.
            </p>
          </HowWeKnow>
        </div>
        <div className="column colophon">
          <p>
            Sources:{" "}
            {payload.sources.map((source, index) => (
              <span key={source.id}>
                {index > 0 ? " · " : ""}
                <a href={source.url}>{source.title}</a>
              </span>
            ))}
          </p>
          <p>
            Built from the Government of India’s public-use microdata; selected estimates checked
            against direct official counterparts; all comparisons descriptive. 2023-24 reference periods
            differ slightly across surveys.
          </p>
          <p>
            <a href="https://github.com/smar98/tamil-nadu-manufacturing-structure">Code, methods and validation register on GitHub</a>
          </p>
          <p>
            US dollar figures use ₹{USD_RATE} to the dollar, approximately the 2023-24 average
            market rate, and are rounded; rupee figures are the estimates.
          </p>
          <p>
            Built by <a href="https://github.com/smar98">Sanchit Mardia</a>.
          </p>
        </div>
      </section>
    </main>
  );
}
