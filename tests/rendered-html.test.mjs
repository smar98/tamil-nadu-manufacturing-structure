import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import test from "node:test";

test("static export renders the structural snapshot", async () => {
  const html = await readFile(new URL("../out/index.html", import.meta.url), "utf8");
  assert.match(html, /<title>Tamil Nadu Manufacturing: A Structural Snapshot<\/title>/i);
  assert.match(html, /Loading the manufacturing structure/i);
  assert.match(html, /\/tamil-nadu-manufacturing-structure\/_next\//i);
  assert.doesNotMatch(html, /Your site is taking shape|react-loading-skeleton/i);
});

test("all published-table reconciliation gates pass", async () => {
  const raw = await readFile(new URL("../public/data/manufacturing-structure.json", import.meta.url), "utf8");
  const data = JSON.parse(raw);
  assert.equal(data.validation.length, 10);
  assert.ok(data.validation.every((check) => check.status === "pass"));
  assert.equal(data.headline.unincorporated_establishments, 1_391_656);
  assert.equal(data.tiers.oae.estimated_establishments, 1_118_993);
  assert.ok(Math.abs(data.plfs.manufacturing_share - 15.97) < 0.01);
});

test("the output is aggregate-only and preserves methodological warnings", async () => {
  const raw = await readFile(new URL("../public/data/manufacturing-structure.json", import.meta.url), "utf8");
  const data = JSON.parse(raw);
  assert.equal(data.sources.length, 3);
  assert.match(data.meta.comparison_warning, /do not track firm transitions/i);
  assert.match(data.meta.disclosure, /No respondent-level record/i);
  assert.ok(data.asuse_sectors.every((sector) => sector.sample_establishments >= 30));
  assert.ok(data.asi_sectors.every((sector) => sector.sample_factories >= 100));
  assert.ok(!raw.includes("fsu_serial_no"));
});

test("the interface states the estimand and the non-claims", async () => {
  const page = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
  assert.match(page, /Not a tracked/);
  assert.match(page, /return to registration/i);
  assert.match(page, /Not identified/);
  assert.match(page, /cannot estimate a registration effect/i);
  assert.match(page, /independently describes/i);
  assert.match(page, /does not measure firm transitions/i);
  assert.match(page, /abnormal shortage of medium firms/i);
});

test("the public data directory contains only the canonical payload", async () => {
  const files = await readdir(new URL("../public/data/", import.meta.url));
  assert.deepEqual(files.sort(), ["manufacturing-structure.json"]);
});
