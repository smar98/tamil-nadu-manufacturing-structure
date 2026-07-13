"use client";

import {
  ArrowDown,
  ArrowUpRight,
  BookOpen,
  Check,
  ChevronDown,
  CircleAlert,
  Database,
  Factory,
  FileCheck2,
  FlaskConical,
  Info,
  Layers3,
  Scale,
  X,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

type Tier = {
  label: string;
  sample_establishments?: number;
  sample_factories?: number;
  estimated_establishments?: number;
  estimated_factories?: number;
  estimated_workers?: number;
  persons_engaged?: number;
  workers_per_establishment?: number;
  persons_per_factory?: number;
  gva_per_worker?: number;
  gva_per_person_engaged?: number;
  female_direct_worker_share?: number;
  contract_worker_share?: number;
};

type AsuseSector = {
  nic2: number;
  label: string;
  sample_establishments: number;
  estimated_establishments: number;
  hwe_share: number;
  workers_per_establishment: number;
  gva_per_worker: number;
  computer_use_share: number;
  internet_use_share: number;
  accounts_share: number;
  bank_account_share: number;
};

type AsiSector = {
  id: string;
  label: string;
  estimated_factories: number;
  persons_engaged: number;
  gva_per_person_engaged: number;
  female_direct_worker_share: number;
  contract_worker_share: number;
  rd_factory_share: number;
  training_factory_share: number;
  sample_factories: number;
  stability: string;
};

type Data = {
  meta: { comparison_warning: string; price_basis: string; disclosure: string };
  headline: {
    unincorporated_establishments: number;
    own_account_share: number;
    hired_worker_share: number;
    registered_factories: number;
    productivity_ratio_registered_to_oae: number;
    productivity_ratio_registered_to_hwe: number;
  };
  tiers: { oae: Tier; hwe: Tier; asi: Tier };
  asuse_sectors: AsuseSector[];
  asi_sectors: AsiSector[];
  plfs: {
    sample_workers: number;
    sample_manufacturing_workers: number;
    manufacturing_share: number;
    male_manufacturing_share: number;
    female_manufacturing_share: number;
    rural_manufacturing_share: number;
    urban_manufacturing_share: number;
    manufacturing_status_shares: {
      self_employed: number;
      regular_wage: number;
      casual_labour: number;
    };
  };
  published: {
    asuse: {
      oae_productivity: number;
      hwe_productivity: number;
    };
  };
  uncertainty: {
    asuse_all_activity_gva_per_worker: number;
    asuse_all_activity_rse_percent: number;
    asuse_manufacturing_gva_per_worker: number;
    asuse_manufacturing_rse_percent: number;
    method: string;
  };
  validation: Array<{
    check: string;
    reconstructed: number;
    published: number;
    relative_error: number;
    status: string;
  }>;
  sources: Array<{
    id: string;
    title: string;
    coverage: string;
    use: string;
    url: string;
    tables: string;
  }>;
};

const formatInteger = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });
const formatOne = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 1 });

function compact(value: number) {
  if (value >= 10_000_000) return `${(value / 10_000_000).toFixed(1)} crore`;
  if (value >= 100_000) return `${(value / 100_000).toFixed(1)} lakh`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(value >= 10_000 ? 0 : 1)}k`;
  return formatInteger.format(value);
}

function rupees(value: number) {
  return `₹${compact(value)}`;
}

function percent(value: number, digits = 1) {
  return `${(value * 100).toFixed(digits)}%`;
}

function SourceTag({ children }: { children: React.ReactNode }) {
  return <span className="source-tag"><Database size={12} />{children}</span>;
}

function TierStage({
  id,
  tier,
  productivity,
  publishedProductivity,
  color,
  active,
}: {
  id: string;
  tier: Tier;
  productivity: number;
  publishedProductivity?: number;
  color: string;
  active: boolean;
}) {
  const count = tier.estimated_establishments ?? tier.estimated_factories ?? 0;
  const people = tier.workers_per_establishment ?? tier.persons_per_factory ?? 0;
  const barHeight = Math.max(8, 100 * productivity / 839_770);
  return (
    <article className={`tier-stage tier-${id} ${active ? "is-active" : ""}`} style={{ "--tier": color } as React.CSSProperties}>
      <div className="tier-number">{id}</div>
      <div className="tier-visual" aria-hidden="true">
        <div className="tier-bar" style={{ height: `${barHeight}%` }}>
          {id === "03" && <Factory size={26} strokeWidth={1.6} />}
        </div>
      </div>
      <div className="tier-copy">
        <p className="eyebrow">{tier.label}</p>
        <strong>{rupees(publishedProductivity ?? productivity)}</strong>
        <span>annual GVA per {id === "03" ? "person engaged" : "worker"}</span>
        <dl>
          <div><dt>Units</dt><dd>{compact(count)}</dd></div>
          <div><dt>People / unit</dt><dd>{formatOne.format(people)}</dd></div>
        </dl>
      </div>
    </article>
  );
}

function StructureVisual({ data }: { data: Data }) {
  const [view, setView] = useState<"productivity" | "scale">("productivity");
  const published = data.published?.asuse;
  return (
    <div className={`structure-visual view-${view}`}>
      <div className="visual-toolbar">
        <div className="segmented" aria-label="Change structure metric">
          <button className={view === "productivity" ? "active" : ""} onClick={() => setView("productivity")}>Productivity</button>
          <button className={view === "scale" ? "active" : ""} onClick={() => setView("scale")}>Enterprise scale</button>
        </div>
        <span className="unit-note">{view === "productivity" ? "2023-24 · current ₹ · linear scale" : "people / unit · log scale"}</span>
      </div>

      <div className="tier-grid">
        <TierStage id="01" tier={data.tiers.oae} productivity={data.tiers.oae.gva_per_worker ?? 0} publishedProductivity={published?.oae_productivity} color="#e9bd45" active={view === "productivity"} />
        <div className="transition-note"><ArrowDown size={16} /><span>Not a tracked<br />firm pipeline</span></div>
        <TierStage id="02" tier={data.tiers.hwe} productivity={data.tiers.hwe.gva_per_worker ?? 0} publishedProductivity={published?.hwe_productivity} color="#de5b45" active={view === "productivity"} />
        <div className="transition-note"><ArrowDown size={16} /><span>Different survey<br />universe</span></div>
        <TierStage id="03" tier={data.tiers.asi} productivity={data.tiers.asi.gva_per_person_engaged ?? 0} color="#17634a" active={view === "productivity"} />
      </div>

      <div className="structure-readout">
        {view === "productivity" ? (
          <p><strong>11.1×</strong> is the descriptive productivity ratio between the reconstructed registered-manufacturing tier and own-account enterprises. It is <em>not</em> the return to registration.</p>
        ) : (
          <p><strong>1.2 → 5.2 → 96.6</strong> people per unit. The sharp discontinuity is the object of inquiry; these cross-sectional surveys cannot tell us which firms successfully scaled.</p>
        )}
      </div>
    </div>
  );
}

function SectorPlot({ data }: { data: Data }) {
  const eligible = useMemo(
    () => data.asuse_sectors.filter((row) => row.sample_establishments >= 100).slice(0, 14),
    [data],
  );
  const [selected, setSelected] = useState(eligible[0]?.nic2 ?? 14);
  const current = eligible.find((row) => row.nic2 === selected) ?? eligible[0];
  const maxGva = Math.max(...eligible.map((row) => row.gva_per_worker));
  const maxEst = Math.max(...eligible.map((row) => row.estimated_establishments));

  return (
    <div className="sector-explorer">
      <div className="plot-wrap">
        <div className="plot-label y-label">Higher labor productivity <ArrowUpRight size={14} /></div>
        <svg className="bubble-plot" viewBox="0 0 760 430" role="img" aria-label="Unincorporated manufacturing sectors by employer share, productivity and number of establishments">
          {[0, 1, 2, 3, 4].map((line) => (
            <g key={`h${line}`}>
              <line x1="56" x2="730" y1={64 + line * 75} y2={64 + line * 75} className="gridline" />
              <text x="47" y={68 + line * 75} textAnchor="end" className="tick-text">{rupees(maxGva * (1 - line / 4))}</text>
            </g>
          ))}
          {[0, 1, 2, 3, 4].map((line) => (
            <g key={`v${line}`}>
              <line y1="40" y2="370" x1={56 + line * 168.5} x2={56 + line * 168.5} className="gridline" />
              <text x={56 + line * 168.5} y="386" textAnchor="middle" className="tick-text">{line * 25}%</text>
            </g>
          ))}
          <text x="56" y="400" className="axis-text">Mostly own-account</text>
          <text x="730" y="400" textAnchor="end" className="axis-text">More hired-worker enterprises</text>
          {eligible.map((row) => {
            const x = 56 + row.hwe_share * 674;
            const y = 364 - (row.gva_per_worker / maxGva) * 300;
            const radius = 8 + 24 * Math.sqrt(row.estimated_establishments / maxEst);
            const isSelected = row.nic2 === selected;
            return (
              <g key={row.nic2} className={`bubble ${isSelected ? "selected" : ""}`} onClick={() => setSelected(row.nic2)} role="button" tabIndex={0} onKeyDown={(event) => event.key === "Enter" && setSelected(row.nic2)}>
                <circle cx={x} cy={y} r={radius} />
                {(isSelected || radius > 20) && <text x={x} y={y + radius + 17} textAnchor="middle">{row.label}</text>}
              </g>
            );
          })}
        </svg>
      </div>

      {current && (
        <aside className="sector-readout">
          <div>
            <span className="nic-label">NIC {current.nic2}</span>
            <h3>{current.label}</h3>
            <p>{compact(current.estimated_establishments)} estimated unincorporated establishments; {formatInteger.format(current.sample_establishments)} sampled.</p>
          </div>
          <dl className="metric-list">
            <div><dt>Hire a regular worker</dt><dd>{percent(current.hwe_share)}</dd></div>
            <div><dt>GVA per worker</dt><dd>{rupees(current.gva_per_worker)}</dd></div>
            <div><dt>Use internet</dt><dd>{percent(current.internet_use_share)}</dd></div>
            <div><dt>Maintain a bank account</dt><dd>{percent(current.bank_account_share)}</dd></div>
          </dl>
          <p className="caution"><CircleAlert size={15} /> Sector points are descriptive estimates. No sector is ranked when fewer than 100 establishments were sampled.</p>
        </aside>
      )}
    </div>
  );
}

function WorkerCheck({ data }: { data: Data }) {
  const status = data.plfs.manufacturing_status_shares;
  return (
    <div className="worker-check">
      <div className="waffle-panel">
        <div className="waffle" aria-label={`${data.plfs.manufacturing_share.toFixed(1)} percent of Tamil Nadu workers are in manufacturing`}>
          {Array.from({ length: 100 }, (_, index) => <span key={index} className={index < Math.round(data.plfs.manufacturing_share) ? "filled" : ""} />)}
        </div>
        <div className="waffle-stat"><strong>{data.plfs.manufacturing_share.toFixed(1)}%</strong><span>of usually working people in Tamil Nadu are in manufacturing</span></div>
      </div>
      <div className="status-panel">
        <p className="eyebrow">Within manufacturing employment</p>
        <div className="status-bar" aria-label="Employment status distribution">
          <span className="regular" style={{ width: percent(status.regular_wage) }} />
          <span className="self" style={{ width: percent(status.self_employed) }} />
          <span className="casual" style={{ width: percent(status.casual_labour) }} />
        </div>
        <div className="status-legend">
          <div><i className="regular" /><strong>{percent(status.regular_wage)}</strong><span>regular wage</span></div>
          <div><i className="self" /><strong>{percent(status.self_employed)}</strong><span>self-employed</span></div>
          <div><i className="casual" /><strong>{percent(status.casual_labour)}</strong><span>casual labor</span></div>
        </div>
        <p className="interpretation">PLFS independently finds both a large wage workforce and a substantial self-employed base. That supports the broad composition story only; it does not corroborate the enterprise counts, productivity gap or a failure to scale.</p>
      </div>
    </div>
  );
}

function MethodsDrawer({ data, onClose }: { data: Data; onClose: () => void }) {
  return (
    <div className="drawer-backdrop" onMouseDown={onClose}>
      <aside className="methods-drawer" onMouseDown={(event) => event.stopPropagation()} aria-modal="true" role="dialog" aria-label="Methods and sources">
        <div className="drawer-head">
          <div><p className="eyebrow">Audit trail</p><h2>Methods & sources</h2></div>
          <button className="icon-button" onClick={onClose} aria-label="Close methods"><X size={20} /></button>
        </div>
        <div className="drawer-body">
          <section>
            <h3>What is estimated</h3>
            <p>All unit-data results use the public-use survey multiplier. Ratios are ratios of weighted totals, not averages of establishment-level ratios. ASUSE monetary records are annualized from each unit’s declared reference period.</p>
          </section>
          <section>
            <h3>What is not identified</h3>
            <p>No common firm identifier links ASUSE to ASI. The dashboard cannot estimate a registration effect, a firm transition rate, the causal return to scaling or whether Tamil Nadu has an abnormal shortage of medium firms.</p>
          </section>
          <section>
            <h3>Sampling uncertainty</h3>
            <p>The design-based RSE of Tamil Nadu manufacturing GVA per worker is <strong>{data.uncertainty.asuse_manufacturing_rse_percent.toFixed(2)}%</strong>. The implementation uses MoSPI’s Appendix B ratio-variance formula and reproduces the published all-activity RSE within its predeclared tolerance. Detailed sector points remain descriptive.</p>
          </section>
          <section>
            <h3>Validation gates</h3>
            <div className="validation-list">
              {data.validation.map((row) => (
                <div key={row.check}><Check size={15} /><span>{row.check}</span><strong>{(row.relative_error * 100).toFixed(2)}% error</strong></div>
              ))}
            </div>
          </section>
          <section>
            <h3>Source ledger</h3>
            {data.sources.map((source) => (
              <article className="source-row" key={source.id}>
                <div><SourceTag>{source.id.toUpperCase()}</SourceTag><h4>{source.title}</h4></div>
                <p>{source.coverage}</p>
                <p><strong>Used for:</strong> {source.use}</p>
                <p className="table-ref">{source.tables}</p>
                <a href={source.url} target="_blank" rel="noreferrer">Open official source <ArrowUpRight size={14} /></a>
              </article>
            ))}
          </section>
        </div>
      </aside>
    </div>
  );
}

export default function Home() {
  const [data, setData] = useState<Data | null>(null);
  const [methodsOpen, setMethodsOpen] = useState(false);

  useEffect(() => {
    const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
    fetch(`${basePath}/data/manufacturing-structure.json`).then((response) => response.json()).then(setData);
  }, []);

  if (!data) {
    return <main className="loading"><Factory size={28} /><span>Loading the manufacturing structure…</span></main>;
  }

  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#top"><span>TN</span><strong>Manufacturing Structure</strong></a>
        <nav>
          <a href="#sectors">Sectors</a>
          <a href="#workers">Workers</a>
          <button onClick={() => setMethodsOpen(true)}><BookOpen size={15} /> Methods</button>
        </nav>
      </header>

      <section className="opening" id="top">
        <div className="opening-copy">
          <p className="kicker"><span /> Tamil Nadu · Manufacturing · 2023-24</p>
          <h1>Tamil Nadu’s<br /><em>manufacturing structure</em></h1>
          <p className="lede"><strong>Four in five</strong> unincorporated manufacturers hire no regular worker. Registered factories operate in a different survey universe and at a much larger average scale. This is a structural comparison, not a tracked path from one tier to another.</p>
          <div className="headline-stat">
            <strong>{compact(data.headline.unincorporated_establishments)}</strong>
            <span>unincorporated manufacturing establishments</span>
            <SourceTag>ASUSE 2023-24</SourceTag>
          </div>
          <a className="down-link" href="#structure">Read the evidence <ChevronDown size={17} /></a>
        </div>
        <div className="opening-diagram" aria-label="80 percent own-account and 20 percent hired-worker unincorporated establishments">
          <div className="share-title"><span>Unincorporated manufacturers</span><strong>100 establishments</strong></div>
          <div className="unit-field">
            {Array.from({ length: 100 }, (_, index) => <span key={index} className={index < 80 ? "oae" : "hwe"}>{index < 80 ? "·" : "+"}</span>)}
          </div>
          <div className="share-legend">
            <div><i className="oae" /><strong>80.4%</strong><span>Own-account<br />No regular hire</span></div>
            <div><i className="hwe" /><strong>19.6%</strong><span>Hired-worker<br />At least one regular hire</span></div>
          </div>
          <p className="diagram-note"><Info size={14} /> “Own-account” is a survey category, not a synonym for unproductive or illegal.</p>
        </div>
      </section>

      <section className="definitions-band" aria-labelledby="definitions-title">
        <div className="definitions-intro">
          <p className="section-index">READ THIS FIRST</p>
          <h2 id="definitions-title">Three survey labels, in plain language</h2>
          <p>These are statistical categories. They are not rankings of ambition, legality or quality.</p>
        </div>
        <div className="definition-grid">
          <article><span>01</span><h3>Unincorporated manufacturer</h3><p>A business making goods that is not incorporated under the Companies or LLP Acts. It may still have GST, Udyam or other registrations.</p></article>
          <article><span>02</span><h3>Own-account establishment</h3><p>The owner may work with unpaid family helpers but employs no hired worker on a fairly regular basis.</p></article>
          <article><span>03</span><h3>Hired-worker establishment</h3><p>An unincorporated business employing at least one hired worker on a fairly regular basis. It is not automatically a registered factory.</p></article>
        </div>
      </section>

      <section className="structure-band" id="structure">
        <div className="section-head light">
          <div><p className="section-index">01 / STRUCTURE</p><h2>Three tiers. One sharp discontinuity.</h2></div>
          <p>Read left to right as a comparison of enterprise types, not as the journey of the same firm. Bar height encodes annual labor productivity.</p>
        </div>
        <StructureVisual data={data} />
      </section>

      <section className="argument-band">
        <div className="argument-title"><FlaskConical size={22} /><h2>The defensible finding</h2></div>
        <div className="argument-grid">
          <article><span>Observed</span><h3>Scale is highly discontinuous</h3><p>Average people per unit rises from 1.2 to 5.2 to 96.6 across the three measured tiers.</p></article>
          <article><span>Observed</span><h3>Productivity differs sharply</h3><p>GVA per person is higher in employer enterprises and far higher in active registered manufacturing.</p></article>
          <article className="not-proven"><span>Not identified</span><h3>Why the discontinuity exists</h3><p>Selection, capital intensity, sector mix, regulation and firm age may all contribute. This tool does not isolate them.</p></article>
        </div>
      </section>

      <section className="content-section" id="sectors">
        <div className="section-head">
          <div><p className="section-index">02 / SECTOR STRUCTURE</p><h2>Which industries are dominated by owner-operated establishments?</h2></div>
          <p>Each circle is an unincorporated manufacturing division. Position shows employer share and productivity; area shows estimated establishments. This does not measure firm transitions.</p>
        </div>
        <SectorPlot data={data} />
      </section>

      <section className="registered-strip">
        <div className="strip-intro"><Factory size={23} /><div><p className="eyebrow">Inside registered manufacturing</p><h2>Productivity levels differ across industries</h2></div></div>
        <div className="registered-sectors">
          {data.asi_sectors.map((sector) => (
            <article key={sector.id}>
              <span>{sector.label}</span>
              <strong>{rupees(sector.gva_per_person_engaged)}</strong>
              <small>GVA / person engaged</small>
              <div className="mini-meter"><i style={{ width: `${Math.min(100, sector.gva_per_person_engaged / 16_000)}%` }} /></div>
              <p>{compact(sector.persons_engaged)} people · n={sector.sample_factories}</p>
            </article>
          ))}
        </div>
        <p className="strip-note"><Scale size={15} /> These levels are useful as a composition warning, not as proof of technological capability. Capital intensity, prices and industry mix can all affect GVA per person.</p>
      </section>

      <section className="content-section worker-section" id="workers">
        <div className="section-head">
          <div><p className="section-index">03 / WORKER-SIDE CHECK</p><h2>What does the household labor survey add?</h2></div>
          <p>PLFS starts with people rather than establishments. It independently describes manufacturing’s employment share and job-status mix; it does not verify enterprise counts or transitions.</p>
        </div>
        <WorkerCheck data={data} />
      </section>

      <section className="decision-band">
        <div><p className="section-index">04 / POLICY USE</p><h2>Questions Tamil Nadu should test next</h2></div>
        <div className="decision-list">
          <article><span>01</span><div><h3>Separate livelihood policy from scale-up policy</h3><p>Most establishments are own-account livelihoods. A scale program should not assume every micro unit wants or is able to become a factory.</p></div></article>
          <article><span>02</span><div><h3>Diagnose the first regular hire, sector by sector</h3><p>In priority sectors, test whether demand, premises, credit, skills or compliance prevents firms that want to hire from doing so. Low hiring alone is not evidence of a constraint.</p></div></article>
          <article><span>03</span><div><h3>Build the missing longitudinal evidence</h3><p>Link consented UDYAM, GST and state incentive records in a secure research environment to measure transitions and survival. Cross-sections cannot do this.</p></div></article>
        </div>
      </section>

      <section className="methods-preview">
        <div><FileCheck2 size={24} /><h2>Ten calculations reproduce published MoSPI tables.</h2><p>Every headline estimate is generated from the public-use files and checked against the official report before the site data is written.</p></div>
        <button onClick={() => setMethodsOpen(true)}>Inspect methods & source ledger <ArrowUpRight size={16} /></button>
      </section>

      <footer>
        <div className="brand"><span>TN</span><strong>Manufacturing Structure</strong></div>
        <p>ASI, ASUSE and PLFS public-use data · current-price cross-section · no causal claim</p>
        <button onClick={() => setMethodsOpen(true)}><Layers3 size={15} /> Data & methods</button>
      </footer>

      {methodsOpen && <MethodsDrawer data={data} onClose={() => setMethodsOpen(false)} />}
    </main>
  );
}
