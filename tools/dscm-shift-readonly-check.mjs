#!/usr/bin/env node
// DSCM copper LL→FTTH Shift flow: READ-ONLY check of steps 1-3 for one landline.
// See docs/reviews/ll-to-ftth-api-comparison.md §6.
//
//   1. GET  ding/frServiceInfoCheck?subsNbr=<landline>  → subsId
//   2. POST ding/subsShiftingCheckBsnl {subsId}          → shiftingFlag Y/N
//   3. POST ding/qryOfferForShifting   {subsId}          → plan list
//
// Step 4 (subsShiftingBsnl) places a real order and is deliberately NOT here: the only paths
// this script can call are the three in READ_ONLY below.
//
// Run it on the VPS (not from a Claude cloud session). Credentials come from the environment
// only, never the command line, and are never printed:
//
//   DSCM_SESSION=<SESSION cookie value>  node dscm-shift-readonly-check.mjs 07242459222
// or, to log in first:
//   DSCM_STAFF_CODE=... DSCM_STAFF_PWD=... DSCM_ORG_ID=...  node dscm-shift-readonly-check.mjs 07242459222
//
// The output holds only return codes, the subsId, the shifting flag and plan ids/names/prices,
// so it can be pasted back into a chat. Exit code: 0 all three steps answered, 1 anything else.
// Needs Node 18+ (built-in fetch).

const BASE = (process.env.DSCM_BASE || 'https://wsc.cdr.bsnl.co.in/portal/drm/api').replace(/\/+$/, '');
const READ_ONLY = new Set(['ding/frServiceInfoCheck', 'ding/subsShiftingCheckBsnl', 'ding/qryOfferForShifting']);
const TIMEOUT_MS = 30000;

const KNOWN = {
  '0': 'success',
  '1': 'out of service area: the line is not bound to this franchise',
  '7070001': 'BSNL internal/unknown error (the outage seen on 27 Sep 2026)',
  '42001044': 'not in franchise / SPI downstream failure',
  '41600024': 'a required parameter is null',
};

const landline = String(process.argv[2] || '').replace(/[\s-]/g, '');
if (!/^0\d{10}$/.test(landline)) {
  console.error('Usage: node dscm-shift-readonly-check.mjs <landline with STD code, e.g. 07242459222>');
  process.exit(1);
}

// The first value found under `key` anywhere in a response, however BSNL nests it.
function find(obj, key, depth = 0) {
  if (!obj || typeof obj !== 'object' || depth > 8) return undefined;
  if (Object.prototype.hasOwnProperty.call(obj, key) && obj[key] !== null && obj[key] !== '') return obj[key];
  for (const v of Object.values(obj)) {
    const hit = find(v, key, depth + 1);
    if (hit !== undefined) return hit;
  }
  return undefined;
}

// The first array of objects anywhere in a response (the plan list).
function firstList(obj, depth = 0) {
  if (!obj || typeof obj !== 'object' || depth > 8) return null;
  if (Array.isArray(obj)) return obj.length && typeof obj[0] === 'object' ? obj : null;
  for (const v of Object.values(obj)) {
    const hit = firstList(v, depth + 1);
    if (hit) return hit;
  }
  return null;
}

const code = (j) => (j ? String(find(j, 'returnCode') ?? find(j, 'code') ?? '?') : '?');
const msg = (j) => (j ? String(find(j, 'returnMsg') ?? find(j, 'message') ?? find(j, 'msg') ?? '') : '');
const explain = (c) => (KNOWN[c] ? ` (${KNOWN[c]})` : '');

function cookieFrom(res) {
  const all = typeof res.headers.getSetCookie === 'function' ? res.headers.getSetCookie() : [res.headers.get('set-cookie') || ''];
  for (const c of all) {
    const m = /(?:^|[,\s])SESSION=([^;,\s]+)/.exec(c);
    if (m) return m[1];
  }
  return null;
}

async function readJson(res) {
  const text = await res.text();
  try { return { json: JSON.parse(text), text }; } catch { return { json: null, text }; }
}

async function login() {
  const { DSCM_STAFF_CODE: staffCode, DSCM_STAFF_PWD: staffPwd, DSCM_ORG_ID: orgId } = process.env;
  if (!staffCode || !staffPwd || !orgId) {
    console.error('Set DSCM_SESSION, or all of DSCM_STAFF_CODE, DSCM_STAFF_PWD and DSCM_ORG_ID.');
    process.exit(1);
  }
  const res = await fetch(`${BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ staffCode, staffPwd, orgId }),
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });
  const { json, text } = await readJson(res);
  const session = cookieFrom(res);
  console.log(`login: HTTP ${res.status}, returnCode ${code(json)}${explain(code(json))}${session ? ', SESSION cookie received' : ', NO SESSION cookie'}`);
  if (!session) {
    // Show what came back, minus anything that could be the password.
    console.log('  body:', (json ? msg(json) : text.slice(0, 200)).split(staffPwd).join('***'));
    process.exit(1);
  }
  return session;
}

async function call(path, { query = null, body = null, session }) {
  if (!READ_ONLY.has(path)) throw new Error(`refusing ${path}: not a read-only step`);
  const url = `${BASE}/${path}${query ? '?' + new URLSearchParams(query) : ''}`;
  const res = await fetch(url, {
    method: body ? 'POST' : 'GET',
    headers: { Accept: 'application/json', Cookie: `SESSION=${session}`, ...(body ? { 'Content-Type': 'application/json' } : {}) },
    body: body ? JSON.stringify(body) : undefined,
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });
  const { json, text } = await readJson(res);
  const c = code(json);
  console.log(`${path}: HTTP ${res.status}, returnCode ${c}${explain(c)}${msg(json) ? ` - ${msg(json)}` : ''}`);
  if (!json) console.log('  (not JSON) first 200 chars:', text.slice(0, 200));
  return { ok: res.ok && c === '0', json };
}

async function main() {
  console.log(`DSCM Shift read-only check for ${landline}, ${new Date().toISOString()}`);
  const session = process.env.DSCM_SESSION || await login();

  const info = await call('ding/frServiceInfoCheck', { query: { subsNbr: landline }, session });
  const subsId = find(info.json, 'subsId');
  if (!info.ok || !subsId) {
    console.log(`Stopped at step 1: ${subsId ? '' : 'no subsId. '}Steps 2-3 need it.`);
    return 1;
  }
  console.log(`  subsId ${subsId}`);

  const check = await call('ding/subsShiftingCheckBsnl', { body: { subsId }, session });
  console.log(`  shiftingFlag ${find(check.json, 'shiftingFlag') ?? '(absent)'}`);

  const offers = await call('ding/qryOfferForShifting', { body: { subsId }, session });
  const list = firstList(offers.json) || [];
  console.log(`  ${list.length} plan(s)`);
  for (const p of list.slice(0, 20)) {
    const id = p.offerId ?? p.planId ?? p.id ?? '?';
    const name = p.offerName ?? p.planName ?? p.name ?? '';
    const price = p.price ?? p.rentAmount ?? p.amount ?? '';
    console.log(`    ${id}  ${name}${price !== '' ? '  ' + price : ''}`);
  }
  return check.ok && offers.ok ? 0 : 1;
}

main().then((rc) => process.exit(rc), (e) => {
  console.error('failed:', e?.cause?.code || e?.name || '', e?.message || e);
  process.exit(1);
});
