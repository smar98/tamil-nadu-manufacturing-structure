import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import test from "node:test";

function exportedKeys(value, keys = []) {
  if (Array.isArray(value)) {
    for (const item of value) exportedKeys(item, keys);
  } else if (value && typeof value === "object") {
    for (const [key, item] of Object.entries(value)) {
      keys.push(key);
      exportedKeys(item, keys);
    }
  }
  return keys;
}

const identifierKeyPattern = /^(?:(?:respondent|household|person)(?:$|_(?:id|identifier|serial(?:_no)?|no|key|link(?:age)?|hash|uuid))|(?:fsu|psu)(?:$|_(?:serial(?:_no)?|id|code|no))|district(?:$|_(?:code|id|identifier|serial(?:_no)?|no))|dispatch.*(?:serial|_id|_identifier|_no)|dsl|sample_est(?:ablishment)?(?:$|_(?:id|identifier|serial(?:_no)?|no))|.*_design)$/i;

test("static export renders the full narrative without a loading state", async () => {
  const html = await readFile(new URL("../out/index.html", import.meta.url), "utf8");
  assert.match(html, /<title>India(?:&#x27;|')s Factory State: Tamil Nadu(?:&#x27;|')s Manufacturing Paradox, 2023-24<\/title>/i);
  assert.match(html, /more than in any other state/i);
  assert.match(html, /gross value added/i);
  assert.match(html, /not published \(sample too small\)/i);
  assert.match(html, /The finding, up front/i);
  assert.match(html, /= India, same measure/i);
  assert.doesNotMatch(html, /hero-count">[\d,]+\.\d/);
  assert.match(html, /Annual Survey of Unincorporated Sector Enterprises/i);
  assert.match(html, /Sanchit Mardia/i);
  assert.match(html, /\/tamil-nadu-manufacturing-structure\/_next\//i);
  assert.doesNotMatch(html, /NaN/);
  assert.doesNotMatch(html, /Loading the 2023-24 manufacturing evidence|react-loading-skeleton/i);
});

test("all published-table reconciliation gates pass", async () => {
  const raw = await readFile(new URL("../public/data/manufacturing-structure.json", import.meta.url), "utf8");
  const data = JSON.parse(raw);
  assert.equal(data.validation.length, 28);
  assert.ok(data.validation.every((check) => check.status === "pass"));
  assert.equal(data.headline.unincorporated_establishments, 1_391_656);
  assert.equal(data.tiers.oae.estimated_establishments, 1_118_993);
  assert.ok(Math.abs(data.plfs.manufacturing_share - 15.97) < 0.01);
  const checks = new Map(data.validation.map((check) => [check.check, check]));
  assert.ok(Math.abs(checks.get("ASUSE TN manufacturing hired workers").reconstructed - 1_078_944) / 1_078_944 <= 0.001);
  assert.ok(Math.abs(checks.get("ASUSE TN manufacturing annual emoluments per hired worker").reconstructed - 140_133) / 140_133 <= 0.01);
});

test("the output is aggregate-only and preserves methodological warnings", async () => {
  const raw = await readFile(new URL("../public/data/manufacturing-structure.json", import.meta.url), "utf8");
  const data = JSON.parse(raw);
  assert.equal(data.sources.length, 3);
  assert.match(data.meta.comparison_warning, /do not track firm transitions/i);
  assert.match(data.meta.disclosure, /weighted aggregates, labels, unweighted sample counts, validation results and disclosure flags/i);
  assert.match(data.meta.disclosure, /no respondent-level records or linkage identifiers/i);
  assert.ok(data.asuse_sectors.every((sector) => sector.sample_establishments >= 30));
  assert.ok(data.asi_sectors.every((sector) => sector.sample_factories >= 100));
  assert.equal(exportedKeys(data).find((key) => identifierKeyPattern.test(key)), undefined);
  for (const key of [
    "respondent_id",
    "household_serial_no",
    "person_uuid",
    "fsu_serial_no",
    "district_code",
    "dispatch_center_serial",
    "dsl",
    "sample_establishment_id",
    "variance_design",
  ]) {
    assert.match(key, identifierKeyPattern);
  }
});

test("structure_v1 is ordered, disclosure-safe, and internally coherent", async () => {
  const raw = await readFile(new URL("../public/data/manufacturing-structure.json", import.meta.url), "utf8");
  const { structure_v1: structure } = JSON.parse(raw);
  assert.ok(structure);
  assert.deepEqual(
    structure.size_bands.map((band) => band.label),
    ["1", "2-4", "5-9", "10-19", "20-49", "50-99", "100-249", "250+"],
  );
  assert.deepEqual(
    structure.middle_definitions.map((definition) => definition.id),
    ["10-249", "10-99", "20-249", "50-249"],
  );

  const rowGroups = [
    structure.establishment_size,
    structure.middle_diagnostic,
    structure.industry_employment,
    structure.size_industry_employment,
    structure.plfs_enterprise_size,
  ];
  const rows = rowGroups.flat();
  assert.deepEqual(structure.quality.allowed_surveys, ["asi", "asuse", "plfs"]);
  assert.deepEqual(structure.quality.allowed_stability, ["low_precision", "stable", "suppressed"]);
  const allowedSurveys = new Set(structure.quality.allowed_surveys);
  const allowedStability = new Set(structure.quality.allowed_stability);
  assert.ok(rows.every((row) => allowedSurveys.has(row.survey)));
  assert.ok(rows.every((row) => allowedStability.has(row.stability)));
  assert.ok(rows.every((row) => Number.isInteger(row.sample_count) && row.sample_count >= 0));
  assert.ok(rows.filter((row) => row.stability === "suppressed").every((row) => row.suppression_reason));
  for (const survey of ["asuse", "asi"]) {
    const geographies = new Set(
      structure.establishment_size.filter((row) => row.survey === survey).map((row) => row.geography_id),
    );
    assert.ok(geographies.size > 30);
    for (const geography of ["IN", "33", "24", "27", "29", "36", "32"]) {
      assert.ok(geographies.has(geography), `${survey} must include geography ${geography}`);
    }
  }

  for (const row of rows) {
    for (const [key, value] of Object.entries(row)) {
      if ((key.startsWith("estimated_") || key.endsWith("_share")) && value !== null) {
        assert.ok(Number.isFinite(value) && value >= 0, `${key} must be a nonnegative estimate`);
      }
      if (row.stability === "suppressed" && (key.startsWith("estimated_") || key.endsWith("_share"))) {
        assert.equal(value, null, `suppressed ${key} must be null`);
      }
    }
  }

  assert.ok(structure.industry_employment.every((row) => row.nic2 >= 10 && row.nic2 <= 33));
  assert.ok(structure.size_industry_employment.every((row) => row.nic2 >= 10 && row.nic2 <= 33));
  assert.ok(structure.plfs_enterprise_size.every((row) => [1, 2, 3, 4, 9].includes(row.size_code)));
  const asiRows = structure.establishment_size.filter((row) => row.survey === "asi");
  assert.ok(asiRows.every((row) => row.sample_unit === "sample returns"));
  assert.ok(asiRows.some((row) => /equal-allocation approximation/i.test(row.classification_label)));
  assert.ok(asiRows.some((row) => row.classification === "per_return_sensitivity"));
  assert.ok(asiRows.some((row) => row.size_band === "zero-unclassified"));

  const completeGroups = new Map();
  for (const row of structure.establishment_size) {
    const key = `${row.survey}|${row.geography_id}|${row.classification}`;
    const group = completeGroups.get(key) ?? [];
    group.push(row);
    completeGroups.set(key, group);
  }
  const complete = [...completeGroups.values()].filter((group) => group.every((row) => row.stability === "stable"));
  assert.ok(complete.length > 0);
  for (const group of complete) {
    assert.ok(Math.abs(group.reduce((sum, row) => sum + row.unit_share, 0) - 1) < 1e-9);
    assert.ok(Math.abs(group.reduce((sum, row) => sum + row.employment_share, 0) - 1) < 1e-9);
  }

  const plfsGroups = new Map();
  for (const row of structure.plfs_enterprise_size) {
    const group = plfsGroups.get(row.geography_id) ?? [];
    group.push(row);
    plfsGroups.set(row.geography_id, group);
  }
  for (const group of plfsGroups.values()) {
    if (group.every((row) => row.stability === "stable")) {
      assert.ok(Math.abs(group.reduce((sum, row) => sum + row.worker_share, 0) - 1) < 1e-9);
    }
  }

  const uniqueKeys = [
    [structure.establishment_size, (row) => `${row.survey}|${row.geography_id}|${row.classification}|${row.size_band}`],
    [structure.middle_diagnostic, (row) => `${row.survey}|${row.geography_id}|${row.classification}|${row.middle_definition}`],
    [structure.industry_employment, (row) => `${row.survey}|${row.geography_id}|${row.nic2}`],
    [structure.size_industry_employment, (row) => `${row.survey}|${row.geography_id}|${row.nic2}|${row.size_band}`],
    [structure.plfs_enterprise_size, (row) => `${row.geography_id}|${row.size_code}`],
  ];
  for (const [group, keyFor] of uniqueKeys) {
    assert.equal(new Set(group.map(keyFor)).size, group.length, "aggregate row keys must be unique");
  }

  assert.doesNotMatch(
    raw,
    /fsu_serial_no|sample_est(?:ablishment)?_no|dispatch.?serial|\"dsl\"|distcode_perv1|FI_perv1/i,
  );
});

test("Layer 3 outcomes follow the locked concepts and disclosure contract", async () => {
  const raw = await readFile(new URL("../public/data/manufacturing-structure.json", import.meta.url), "utf8");
  const { structure_v1: structure } = JSON.parse(raw);
  const valueRows = structure.value_addition;
  const compensationRows = structure.establishment_compensation;
  assert.ok(valueRows.length > 0);
  assert.ok(compensationRows.length > 0);
  assert.match(structure.metadata.layer3.price_basis, /Current rupees/i);
  assert.match(structure.metadata.layer3.dimensions, /No size-by-industry outcomes/i);
  assert.match(structure.metadata.layer3.asi_labour_cost_proxy, /welfare is not necessarily cash pay/i);

  const allowedDimensions = new Set(["overall", "size", "industry"]);
  const allowedSurveys = new Set(["asuse", "asi"]);
  const shareFieldFor = (rows) => rows === valueRows ? "gva_contribution_share" : "compensation_contribution_share";

  for (const rows of [valueRows, compensationRows]) {
    const shareField = shareFieldFor(rows);
    for (const row of rows) {
      assert.ok(allowedSurveys.has(row.survey));
      assert.ok(allowedDimensions.has(row.dimension));
      assert.ok(["stable", "suppressed"].includes(row.stability));
      assert.equal(typeof row.denominator_positive, "boolean");
      assert.equal(typeof row.per_person_label, "string");
      assert.ok(Object.hasOwn(row, "per_person_value"));
      assert.ok(Object.hasOwn(row, shareField));
      assert.ok(row.weighted_denominator_concentration >= 0 && row.weighted_denominator_concentration <= 1);
      assert.ok(row.absolute_weighted_numerator_concentration >= 0 && row.absolute_weighted_numerator_concentration <= 1);
      assert.ok(!Object.keys(row).some((key) => [
        "annual_gva", "gva", "annual_emoluments", "emoluments", "compensation_employees",
      ].includes(key)), "Layer 3 must not publish raw monetary totals");
      assert.ok(!(Object.hasOwn(row, "size_band") && Object.hasOwn(row, "nic2")));
      if (row.dimension === "overall") assert.equal(row[shareField], null);

      const disclosureTrigger = row.sample_count < 10
        || row.weighted_denominator_concentration > 0.70
        || row.absolute_weighted_numerator_concentration > 0.70;
      assert.equal(row.stability === "suppressed", disclosureTrigger);
      if (row.stability === "suppressed") {
        assert.equal(row.per_person_value, null);
        assert.equal(row[shareField], null);
        if (Object.hasOwn(row, "labour_cost_proxy_share_of_gva")) {
          assert.equal(row.labour_cost_proxy_share_of_gva, null);
        }
      }
      if (!row.denominator_positive) assert.equal(row.per_person_value, null);
      if (row.per_person_value !== null) assert.ok(Number.isFinite(row.per_person_value));
      if (row[shareField] !== null) assert.ok(Number.isFinite(row[shareField]));
    }
  }

  assert.deepEqual(
    new Set(valueRows.filter((row) => row.survey === "asuse").map((row) => row.per_person_label)),
    new Set(["GVA per worker in market establishments"]),
  );
  assert.deepEqual(
    new Set(valueRows.filter((row) => row.survey === "asi").map((row) => row.per_person_label)),
    new Set(["GVA per person engaged"]),
  );
  const conceptLabels = new Map([
    ["annual_emoluments", "Annual emoluments per hired worker"],
    ["emoluments", "Emoluments per paid person engaged"],
    ["labour_cost_proxy", "Labour-cost proxy per paid person engaged"],
  ]);
  assert.deepEqual(new Set(compensationRows.map((row) => row.concept)), new Set(conceptLabels.keys()));
  assert.ok(compensationRows.every((row) => row.per_person_label === conceptLabels.get(row.concept)));
  assert.ok(compensationRows.filter((row) => row.survey === "asuse").every((row) => row.concept === "annual_emoluments"));
  assert.ok(compensationRows.filter((row) => row.survey === "asi").every((row) => ["emoluments", "labour_cost_proxy"].includes(row.concept)));
  for (const row of compensationRows) {
    const hasProxyShare = Object.hasOwn(row, "labour_cost_proxy_share_of_gva");
    assert.equal(hasProxyShare, row.survey === "asi" && row.concept === "labour_cost_proxy");
    if (hasProxyShare && !row.aggregate_gva_positive) {
      assert.equal(row.labour_cost_proxy_share_of_gva, null);
    }
  }

  for (const rows of [valueRows, compensationRows]) {
    const keys = rows.map((row) => [
      row.survey, row.concept ?? "", row.dimension, row.geography_id,
      row.classification ?? "", row.size_band ?? "", row.nic2 ?? "",
    ].join("|"));
    assert.equal(new Set(keys).size, rows.length, "Layer 3 row keys must be unique");
  }

  let reconciledGroups = 0;
  for (const rows of [valueRows, compensationRows]) {
    const shareField = shareFieldFor(rows);
    const groups = new Map();
    for (const row of rows.filter((candidate) => candidate.dimension !== "overall")) {
      const key = [
        row.survey, row.concept ?? "", row.dimension, row.geography_id,
        row.classification ?? "",
      ].join("|");
      const siblings = groups.get(key) ?? [];
      siblings.push(row);
      groups.set(key, siblings);
    }
    for (const siblings of groups.values()) {
      const shares = siblings.map((row) => row[shareField]);
      if (siblings.some((row) => row.stability === "suppressed")) {
        assert.ok(shares.every((share) => share === null));
      } else {
        assert.ok(shares.every((share) => share === null) || shares.every((share) => share !== null));
        if (shares.every((share) => share !== null)) {
          assert.ok(Math.abs(shares.reduce((sum, share) => sum + share, 0) - 1) < 1e-9);
          reconciledGroups += 1;
        }
      }
    }
  }
  assert.ok(reconciledGroups > 0);

  for (const rows of [valueRows, compensationRows]) {
    const overall = new Map(
      rows
        .filter((row) => row.survey === "asi" && row.dimension === "overall")
        .map((row) => [`${row.geography_id}|${row.concept ?? ""}`, row.sample_count]),
    );
    const sensitivityGroups = new Map();
    for (const row of rows.filter((candidate) => candidate.survey === "asi" && candidate.dimension === "size")) {
      const key = `${row.geography_id}|${row.concept ?? ""}|${row.classification}`;
      const group = sensitivityGroups.get(key) ?? [];
      group.push(row);
      sensitivityGroups.set(key, group);
    }
    for (const [key, group] of sensitivityGroups) {
      const [geographyId, concept] = key.split("|");
      assert.equal(
        group.reduce((sum, row) => sum + row.sample_count, 0),
        overall.get(`${geographyId}|${concept}`),
        `ASI size classification must partition the overall sample for ${key}`,
      );
    }
  }

  for (const rows of [valueRows, compensationRows]) {
    for (const survey of ["asuse", "asi"]) {
      const overallGeographies = new Set(rows.filter((row) => row.survey === survey && row.dimension === "overall").map((row) => row.geography_id));
      const sizeGeographies = new Set(rows.filter((row) => row.survey === survey && row.dimension === "size").map((row) => row.geography_id));
      assert.ok(overallGeographies.size > 30);
      assert.deepEqual(sizeGeographies, overallGeographies);
      for (const geography of ["IN", "33", "24", "27", "29", "36", "32"]) {
        assert.ok(overallGeographies.has(geography), `${survey} Layer 3 must include geography ${geography}`);
      }
    }
  }

  const industryGeographies = new Set(["IN", "33", "24", "27", "29", "36", "32"]);
  assert.deepEqual(new Set(valueRows.filter((row) => row.dimension === "industry").map((row) => row.geography_id)), industryGeographies);
  assert.deepEqual(new Set(compensationRows.filter((row) => row.dimension === "industry").map((row) => row.geography_id)), industryGeographies);
  assert.doesNotMatch(
    JSON.stringify({ valueRows, compensationRows }),
    /fsu_serial_no|sample_est(?:ablishment)?_no|dispatch.?serial|"dsl"|distcode_perv1|FI_perv1/i,
  );
});

test("Layer 4 follows the locked PLFS concepts, design and suppression contract", async () => {
  const raw = await readFile(new URL("../public/data/manufacturing-structure.json", import.meta.url), "utf8");
  const data = JSON.parse(raw);
  const { structure_v1: structure } = data;
  const earnings = structure.worker_earnings;
  const jobQuality = structure.worker_job_quality;
  assert.ok(earnings.length > 0);
  assert.ok(jobQuality.length > 0);
  assert.match(structure.metadata.layer4.earnings_activity_concept, /current weekly status/i);
  assert.match(structure.metadata.layer4.job_quality_activity_concept, /principal-activity precedence/i);
  assert.match(structure.metadata.layer4.sex_convention, /codes 1 and 3/i);
  assert.match(structure.metadata.layer4.dimensions, /Earnings by enterprise size are not produced/i);
  assert.match(structure.metadata.layer4.uncertainty, /two-interpenetrating-subsample/i);

  const earningsConcepts = new Map([
    ["regular_monthly_earnings", ["rupees per month", "preceding calendar month", "persons"]],
    ["self_employment_30_day_gross_earnings", ["rupees per 30 days (gross)", "last 30 days", "persons"]],
    ["casual_person_day_earnings", ["rupees per person-day", "previous 7 days", "person-days"]],
  ]);
  const jobConcepts = new Set([
    "written_contract", "paid_leave", "specified_social_security",
    "no_social_security", "unknown_social_security",
  ]);
  assert.deepEqual(new Set(earnings.map((row) => row.concept)), new Set(earningsConcepts.keys()));
  assert.deepEqual(new Set(jobQuality.map((row) => row.concept)), jobConcepts);
  assert.ok(earnings.every((row) => ["overall", "sex", "sector"].includes(row.dimension)));
  assert.ok(!earnings.some((row) => row.dimension === "enterprise_size"));
  assert.ok(jobQuality.every((row) => ["overall", "sex", "sector", "enterprise_size"].includes(row.dimension)));
  assert.ok(jobQuality.filter((row) => row.dimension === "enterprise_size").every((row) => ["1", "2", "3", "4", "9"].includes(row.category_id)));

  const commonFields = [
    "survey", "year", "concept", "concept_label", "dimension", "geography_id",
    "geography_label", "geography_type", "category_id", "category_label", "estimate",
    "unit", "recall_period", "sample_unit", "sample_count", "active_fsu_count",
    "kish_effective_n", "maximum_weight_share", "standard_error", "rse",
    "ci95_lower", "ci95_upper", "stability", "suppression_reason",
  ];
  for (const row of [...earnings, ...jobQuality]) {
    assert.equal(row.survey, "plfs");
    assert.ok(commonFields.every((field) => Object.hasOwn(row, field)));
    assert.ok(Number.isInteger(row.sample_count) && row.sample_count >= 0);
    assert.ok(Number.isInteger(row.active_fsu_count) && row.active_fsu_count >= 0);
    assert.ok(Number.isFinite(row.kish_effective_n) && row.kish_effective_n >= 0);
    assert.ok(row.maximum_weight_share >= 0 && row.maximum_weight_share <= 1);
    assert.ok(["stable", "low_precision", "suppressed"].includes(row.stability));
    if (row.sample_count < 30 || row.active_fsu_count < 10 || row.kish_effective_n < 30 || row.maximum_weight_share > 0.20) {
      assert.equal(row.stability, "suppressed");
    }
    if (row.stability === "suppressed") {
      assert.equal(row.estimate, null);
      assert.equal(row.standard_error, null);
      assert.equal(row.rse, null);
      assert.equal(row.ci95_lower, null);
      assert.equal(row.ci95_upper, null);
      assert.equal(typeof row.suppression_reason, "string");
    } else {
      assert.ok(Number.isFinite(row.estimate));
      assert.ok(Number.isFinite(row.standard_error) && row.standard_error >= 0);
      assert.ok(Number.isFinite(row.rse) && row.rse >= 0 && row.rse <= 0.30);
      assert.ok(row.ci95_lower <= row.estimate && row.estimate <= row.ci95_upper);
      assert.ok(row.sample_count >= 30);
      assert.ok(row.active_fsu_count >= 10);
      assert.ok(row.kish_effective_n >= 30);
      assert.ok(row.maximum_weight_share <= 0.20);
      if (row.stability === "stable") assert.ok(row.rse <= 0.20);
      if (row.stability === "low_precision") assert.ok(row.rse > 0.20 && row.rse <= 0.30);
    }
  }

  for (const row of earnings) {
    const [unit, recallPeriod, sampleUnit] = earningsConcepts.get(row.concept);
    assert.equal(row.unit, unit);
    assert.equal(row.recall_period, recallPeriod);
    assert.equal(row.sample_unit, sampleUnit);
    assert.ok(Object.hasOwn(row, "maximum_weighted_outcome_share"));
    assert.ok(!Object.hasOwn(row, "unweighted_yes_count"));
    assert.ok(!Object.hasOwn(row, "unweighted_no_count"));
    assert.ok(row.maximum_weighted_outcome_share >= 0 && row.maximum_weighted_outcome_share <= 1);
    if (row.maximum_weighted_outcome_share > 0.20) assert.equal(row.stability, "suppressed");
    if (row.stability !== "suppressed") {
      assert.ok(row.maximum_weighted_outcome_share <= 0.20);
      if (["regular_monthly_earnings", "casual_person_day_earnings"].includes(row.concept)) {
        assert.ok(row.ci95_lower >= 0);
      }
    }
  }
  for (const row of jobQuality) {
    assert.equal(row.unit, "proportion");
    assert.equal(row.sample_unit, "persons");
    assert.match(row.recall_period, /usual status/i);
    assert.ok(Object.hasOwn(row, "unweighted_yes_count"));
    assert.ok(Object.hasOwn(row, "unweighted_no_count"));
    assert.ok(!Object.hasOwn(row, "maximum_weighted_outcome_share"));
    assert.equal(row.unweighted_yes_count + row.unweighted_no_count, row.sample_count);
    if (row.unweighted_yes_count < 10 || row.unweighted_no_count < 10) assert.equal(row.stability, "suppressed");
    if (row.stability !== "suppressed") {
      assert.ok(row.unweighted_yes_count >= 10);
      assert.ok(row.unweighted_no_count >= 10);
      assert.ok(row.estimate >= 0 && row.estimate <= 1);
      assert.ok(row.ci95_lower >= 0 && row.ci95_upper <= 1);
    }
  }

  const requiredSubgroupGeographies = new Set(["IN", "33", "24", "27", "29", "36", "32"]);
  for (const rows of [earnings, jobQuality]) {
    const concepts = new Set(rows.map((row) => row.concept));
    let expectedOverall;
    for (const concept of concepts) {
      const overall = new Set(rows.filter((row) => row.concept === concept && row.dimension === "overall").map((row) => row.geography_id));
      assert.ok(overall.size > 30);
      for (const geography of requiredSubgroupGeographies) assert.ok(overall.has(geography));
      if (expectedOverall) assert.deepEqual(overall, expectedOverall);
      expectedOverall = overall;
      for (const dimension of ["sex", "sector", ...(rows === jobQuality ? ["enterprise_size"] : [])]) {
        assert.deepEqual(
          new Set(rows.filter((row) => row.concept === concept && row.dimension === dimension).map((row) => row.geography_id)),
          requiredSubgroupGeographies,
        );
      }
    }
  }

  const socialConcepts = new Set([
    "specified_social_security", "no_social_security", "unknown_social_security",
  ]);
  const socialGroups = new Map();
  for (const row of jobQuality.filter((candidate) => socialConcepts.has(candidate.concept))) {
    const key = [row.dimension, row.geography_id, row.category_id].join("|");
    const group = socialGroups.get(key) ?? [];
    group.push(row);
    socialGroups.set(key, group);
  }
  let completeSocialGroups = 0;
  for (const group of socialGroups.values()) {
    assert.equal(group.length, 3);
    assert.equal(new Set(group.map((row) => row.sample_count)).size, 1);
    const published = group.filter((row) => row.stability !== "suppressed");
    if (published.length === 3) {
      assert.ok(Math.abs(published.reduce((sum, row) => sum + row.estimate, 0) - 1) < 1e-9);
      completeSocialGroups += 1;
    }
  }
  assert.ok(completeSocialGroups > 0);
  const tnSocialHeadlines = jobQuality.filter(
    (row) => row.geography_id === "33" && row.dimension === "overall" && socialConcepts.has(row.concept),
  );
  assert.ok(tnSocialHeadlines.find((row) => row.concept === "specified_social_security").estimate !== null);
  assert.ok(tnSocialHeadlines.find((row) => row.concept === "no_social_security").estimate !== null);
  assert.equal(tnSocialHeadlines.find((row) => row.concept === "unknown_social_security").estimate, null);

  for (const rows of [earnings, jobQuality]) {
    const keys = rows.map((row) => [
      row.concept, row.dimension, row.geography_id, row.category_id,
    ].join("|"));
    assert.equal(new Set(keys).size, rows.length, "Layer 4 row keys must be unique");
  }

  const validationNames = new Set(data.validation.map((check) => check.check));
  for (const fragment of [
    "PLFS Table 36 India no written contract",
    "PLFS Table 36 Tamil Nadu no written contract",
    "PLFS Table 37 enterprise size",
    "PLFS Table 37 sample total",
    "PLFS Table 51 manufacturing casual earnings",
    "PLFS TN rural manufacturing share RSE",
  ]) {
    assert.ok([...validationNames].some((name) => name.includes(fragment)), `missing validation gate: ${fragment}`);
  }
  assert.ok(data.validation.every((check) => check.status === "pass"));
  assert.doesNotMatch(
    JSON.stringify({ earnings, jobQuality, layer4: structure.metadata.layer4 }),
    /b1q1_perv1|nss_region_perv1|b1q5_perv1|b1q6_perv1|b1q11_perv1|fsu_serial_no|psu_serial_no|dispatch.?serial|district.?code|person.?id|household.?id|_design/i,
  );
});

test("Layer 5 peer comparisons follow the locked raw and adjustment contract", async () => {
  const publicPath = process.env.LAYER5_PAYLOAD
    ?? new URL("../public/data/manufacturing-structure.json", import.meta.url);
  const raw = await readFile(publicPath, "utf8");
  const data = JSON.parse(raw);
  const structure = data.structure_v1;
  assert.ok(Array.isArray(structure.peer_comparisons_raw), "Layer 5 raw comparisons are required");
  assert.ok(Array.isArray(structure.peer_comparisons_adjusted), "Layer 5 adjusted comparisons are required");

  const rawRows = structure.peer_comparisons_raw;
  const adjustedRows = structure.peer_comparisons_adjusted;
  const comparators = new Set(["IN", "24", "27", "29", "36", "32"]);
  const proportionOutcomes = new Set([
    "labour_cost_proxy_share_of_gva", "written_contract", "paid_leave",
    "specified_social_security", "no_social_security",
  ]);
  const expectedRawOutcomes = new Set([
    "gva_per_worker", "annual_emoluments_per_hired_worker",
    "gva_per_person_engaged", "emoluments_per_paid_person_engaged",
    "labour_cost_proxy_per_paid_person_engaged", "labour_cost_proxy_share_of_gva",
    "regular_monthly_earnings", "self_employment_30_day_gross_earnings",
    "casual_person_day_earnings", "written_contract", "paid_leave",
    "specified_social_security", "no_social_security",
  ]);
  assert.equal(rawRows.length, expectedRawOutcomes.size * comparators.size);
  assert.deepEqual(new Set(rawRows.map((row) => row.outcome)), expectedRawOutcomes);
  for (const outcome of expectedRawOutcomes) {
    assert.deepEqual(
      new Set(rawRows.filter((row) => row.outcome === outcome).map((row) => row.comparator_id)),
      comparators,
    );
  }
  assert.equal(
    new Set(rawRows.map((row) => `${row.outcome}|${row.comparator_id}`)).size,
    rawRows.length,
  );

  const sourceSpec = new Map([
    ["gva_per_worker", ["value_addition", "asuse", null, "per_person_value"]],
    ["annual_emoluments_per_hired_worker", ["establishment_compensation", "asuse", "annual_emoluments", "per_person_value"]],
    ["gva_per_person_engaged", ["value_addition", "asi", null, "per_person_value"]],
    ["emoluments_per_paid_person_engaged", ["establishment_compensation", "asi", "emoluments", "per_person_value"]],
    ["labour_cost_proxy_per_paid_person_engaged", ["establishment_compensation", "asi", "labour_cost_proxy", "per_person_value"]],
    ["labour_cost_proxy_share_of_gva", ["establishment_compensation", "asi", "labour_cost_proxy", "labour_cost_proxy_share_of_gva"]],
    ["regular_monthly_earnings", ["worker_earnings", "plfs", "regular_monthly_earnings", "estimate"]],
    ["self_employment_30_day_gross_earnings", ["worker_earnings", "plfs", "self_employment_30_day_gross_earnings", "estimate"]],
    ["casual_person_day_earnings", ["worker_earnings", "plfs", "casual_person_day_earnings", "estimate"]],
    ["written_contract", ["worker_job_quality", "plfs", "written_contract", "estimate"]],
    ["paid_leave", ["worker_job_quality", "plfs", "paid_leave", "estimate"]],
    ["specified_social_security", ["worker_job_quality", "plfs", "specified_social_security", "estimate"]],
    ["no_social_security", ["worker_job_quality", "plfs", "no_social_security", "estimate"]],
  ]);
  const sourceRow = (row, geographyId) => {
    const [arrayName, survey, concept] = sourceSpec.get(row.outcome);
    const matches = structure[arrayName].filter((source) => (
      source.survey === survey
      && source.dimension === "overall"
      && source.geography_id === geographyId
      && (source.concept ?? null) === concept
    ));
    assert.equal(matches.length, 1, `one source row required for ${row.outcome}/${geographyId}`);
    return matches[0];
  };
  for (const row of rawRows) {
    const [, , , valueField] = sourceSpec.get(row.outcome);
    const tnSource = sourceRow(row, "33");
    const comparatorSource = sourceRow(row, row.comparator_id);
    assert.equal(row.tn_estimate, tnSource[valueField]);
    assert.equal(row.comparator_estimate, comparatorSource[valueField]);
    assert.equal(row.is_proportion, proportionOutcomes.has(row.outcome));
    assert.equal(row.relative_ratio, row.is_proportion ? null : row.relative_ratio);
    if (row.stability === "suppressed") {
      assert.equal(row.absolute_gap, null);
      assert.equal(row.relative_ratio, null);
      assert.equal(row.relative_gap_percent, null);
      assert.equal(typeof row.suppression_reason, "string");
    } else {
      assert.equal(row.absolute_gap, row.tn_estimate - row.comparator_estimate);
      if (row.is_proportion) {
        assert.equal(row.relative_ratio, null);
        assert.equal(row.relative_gap_percent, null);
        assert.equal(row.gap_display_unit, "percentage_points");
      } else if (row.comparator_estimate > 0) {
        assert.equal(row.relative_ratio, row.tn_estimate / row.comparator_estimate);
        assert.equal(row.relative_gap_percent, 100 * (row.relative_ratio - 1));
      } else {
        assert.equal(row.relative_ratio, null);
        assert.equal(row.relative_gap_percent, null);
      }
    }
    for (const field of ["standard_error", "rse", "ci95_lower", "ci95_upper"]) {
      assert.equal(row[`tn_${field}`], row.survey === "plfs" ? tnSource[field] : null);
      assert.equal(row[`comparator_${field}`], row.survey === "plfs" ? comparatorSource[field] : null);
    }
    assert.ok(!Object.keys(row).some((key) => /gap.*(standard_error|rse|ci|interval)/i.test(key)));
  }

  assert.deepEqual(
    structure.metadata.layer5.industry_classification.groups.flatMap((group) => group.nic2).sort((a, b) => a - b),
    Array.from({ length: 24 }, (_, index) => index + 10),
  );
  assert.deepEqual(
    structure.metadata.layer5.size_classification.groups.flatMap((group) => group.size_bands),
    structure.size_bands.map((band) => band.id),
  );
  assert.match(structure.metadata.layer5.interpretation_boundary, /descriptive/i);
  assert.match(structure.metadata.layer5.uncertainty_note, /no confidence intervals/i);
  assert.equal(structure.metadata.layer5.uncertainty_available, false);

  assert.equal(adjustedRows.length, 78);
  assert.equal(
    new Set(adjustedRows.map((row) => `${row.outcome}|${row.adjustment_dimension}|${row.comparator_id}`)).size,
    adjustedRows.length,
  );
  assert.ok(!adjustedRows.some((row) => row.survey === "plfs"));
  assert.ok(!adjustedRows.some((row) => row.survey === "asuse" && row.adjustment_dimension === "industry_size"));
  assert.ok(!adjustedRows.some((row) => row.outcome === "labour_cost_proxy_share_of_gva"));
  const expectedAdjusted = new Map([
    ["gva_per_worker", new Set(["industry", "size"])],
    ["annual_emoluments_per_hired_worker", new Set(["industry", "size"])],
    ["gva_per_person_engaged", new Set(["industry", "size", "industry_size"])],
    ["emoluments_per_paid_person_engaged", new Set(["industry", "size", "industry_size"])],
    ["labour_cost_proxy_per_paid_person_engaged", new Set(["industry", "size", "industry_size"])],
  ]);
  for (const [outcome, dimensions] of expectedAdjusted) {
    assert.deepEqual(
      new Set(adjustedRows.filter((row) => row.outcome === outcome).map((row) => row.adjustment_dimension)),
      dimensions,
    );
    for (const dimension of dimensions) {
      assert.deepEqual(
        new Set(adjustedRows.filter((row) => row.outcome === outcome && row.adjustment_dimension === dimension).map((row) => row.comparator_id)),
        comparators,
      );
    }
  }

  const nullWhenSuppressed = [
    "full_raw_tn", "full_raw_comparator", "full_raw_gap", "common_support_tn",
    "common_support_comparator", "common_support_raw_gap", "standardized_tn",
    "standardized_comparator", "adjusted_gap", "composition_component",
    "within_component", "decomposition_residual",
  ];
  for (const row of adjustedRows) {
    assert.ok(row.tn_denominator_coverage >= 0 && row.tn_denominator_coverage <= 1);
    assert.ok(row.comparator_denominator_coverage >= 0 && row.comparator_denominator_coverage <= 1);
    assert.ok(Number.isInteger(row.retained_cell_count) && row.retained_cell_count >= 0);
    assert.equal(
      row.total_cell_count,
      row.adjustment_dimension === "industry" ? 7 : row.adjustment_dimension === "size" ? 4 : 28,
    );
    assert.equal(row.uncertainty_available, false);
    if (row.stability === "suppressed") {
      for (const field of nullWhenSuppressed) assert.equal(row[field], null);
      assert.deepEqual(row.components, []);
      assert.equal(typeof row.suppression_reason, "string");
      continue;
    }
    assert.equal(row.stability, "stable");
    assert.equal(row.suppression_reason, null);
    assert.ok(row.tn_denominator_coverage >= 0.95);
    assert.ok(row.comparator_denominator_coverage >= 0.95);
    assert.ok(row.retained_cell_count >= 2);
    assert.equal(row.components.length, row.retained_cell_count);
    assert.ok(row.components.every((component) => Number.isFinite(component.tn_cell_rate) && Number.isFinite(component.comparator_cell_rate)));
    const sum = (field) => row.components.reduce((total, component) => total + component[field], 0);
    assert.ok(Math.abs(sum("tn_weight") - 1) < 1e-9);
    assert.ok(Math.abs(sum("comparator_weight") - 1) < 1e-9);
    assert.ok(Math.abs(sum("common_weight") - 1) < 1e-9);
    assert.ok(Math.abs(row.standardized_tn - row.components.reduce((total, component) => total + component.common_weight * component.tn_cell_rate, 0)) < 1e-8 * Math.max(1, Math.abs(row.standardized_tn)));
    assert.ok(Math.abs(row.standardized_comparator - row.components.reduce((total, component) => total + component.common_weight * component.comparator_cell_rate, 0)) < 1e-8 * Math.max(1, Math.abs(row.standardized_comparator)));
    const tolerance = 1e-8 * Math.max(1, Math.abs(row.common_support_raw_gap));
    assert.ok(Math.abs(row.adjusted_gap - row.within_component) <= tolerance);
    assert.ok(Math.abs(row.common_support_raw_gap - row.composition_component - row.within_component) <= tolerance);
    assert.ok(Math.abs(row.decomposition_residual) <= tolerance);
  }

  assert.equal(data.validation.length, 28);
  assert.ok(data.validation.every((check) => check.status === "pass"));
  assert.doesNotMatch(
    JSON.stringify({ rawRows, adjustedRows, layer5: structure.metadata.layer5 }),
    /respondent|household.?id|person.?id|fsu(?:_serial)?|psu(?:_serial)?|district|dispatch|"dsl"|sample_est(?:ablishment)?_no|_design/i,
  );
  if (!process.env.LAYER5_PAYLOAD) {
    const research = await readFile(new URL("../research/derived/manufacturing-structure.json", import.meta.url), "utf8");
    assert.equal(raw, research);
  } else if (process.env.LAYER5_RESEARCH_PAYLOAD) {
    const research = await readFile(process.env.LAYER5_RESEARCH_PAYLOAD, "utf8");
    assert.equal(raw, research);
  }
});

test("the committed ASI aggregate CSV excludes suppress-grade cells", async () => {
  const raw = await readFile(new URL("../research/derived/asi_aggregates.csv", import.meta.url), "utf8");
  const [header, ...lines] = raw.trim().split(/\r?\n/);
  const stabilityIndex = header.split(",").indexOf("stability");
  assert.ok(stabilityIndex >= 0);
  assert.ok(lines.length > 0);
  assert.ok(lines.every((line) => line.split(",")[stabilityIndex] !== "suppress"));
});

test("the interface states the estimand and the non-claims", async () => {
  const page = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
  // Descriptive, not causal.
  assert.match(page, /identifies\s+causes or evaluates any policy/i);
  assert.match(page, /gap remaining\s+under a common industry/i);
  assert.match(page, /These data do not\s+identify its causes/i);
  // Three separate survey universes that cannot be merged into one firm ladder.
  assert.match(page, /cannot be merged into one ladder from workshop to\s+factory/i);
  assert.match(page, /No common identifier links the three surveys/i);
  assert.match(page, /abnormally few mid-size firms/i);
  // Suppressed values render as an explicit unavailability label, never zero/blank.
  assert.match(page, /not published \(sample too small\)/i);
  // Public claim boundaries.
  assert.match(page, /add less value per person than those in India overall and in each of the\s+five other manufacturing states/i);
  assert.match(page, /gross value added \(GVA\) per person\s+engaged/i);
  assert.match(page, /10–249[\s\S]*10–99[\s\S]*20–249[\s\S]*50–249/i);
  assert.match(page, /does not\s+control products, capital, technology, management, prices or markups/i);
  assert.match(page, /No enacted or\s+notified\s+successor was found as of July 2026/i);
  assert.match(page, /3\.47%/);
  assert.doesNotMatch(page, /nearly the least|largest slice in the country|worker-exploitation|\bsame work\b|same things/i);
});

test("the interface exposes native accessibility semantics", async () => {
  const [page, scrolly, css] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/scrolly.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/globals.css", import.meta.url), "utf8"),
  ]);
  assert.match(page, /<h1>[\s\S]*<CountUp[\s\S]*className="hero-title"[\s\S]*<\/h1>/);
  assert.match(page, /<caption className="sr-only">Results of the 28 predeclared validation checks<\/caption>/);
  assert.match(page, /<th scope="row">\{check\.check\}<\/th>/);
  assert.match(page, /Pass ·/);
  assert.match(page, /<svg aria-hidden="true" focusable="false"/);
  assert.match(page, /className="dense-chart"/);
  assert.match(scrolly, /inert=\{!pastHero\}/);
  assert.match(scrolly, /aria-hidden=\{enhanced \? index !== stateIndex : undefined\}/);
  assert.match(scrolly, /aria-controls=/);
  assert.match(scrolly, /aria-labelledby=/);
  assert.match(scrolly, /tabIndex=\{index === selected \? 0 : -1\}/);
  for (const key of ["ArrowLeft", "ArrowRight", "Home", "End"]) assert.match(scrolly, new RegExp(key));
  assert.match(css, /figure\.dense-chart svg \{ min-width: 45rem; \}/);
  assert.match(css, /\.sr-only/);
});

test("the public data directory contains only the canonical payload", async () => {
  const files = await readdir(new URL("../public/data/", import.meta.url));
  assert.deepEqual(files.sort(), ["manufacturing-structure.json"]);
});
