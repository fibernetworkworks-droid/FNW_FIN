// Drives dscm-shift-readonly-check.mjs against a local mock of the DSCM gateway: no BSNL call.
//   node tools/dscm-shift-readonly-check.test.mjs
import http from 'node:http';
import { execFile } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SCRIPT = fileURLToPath(new URL('./dscm-shift-readonly-check.mjs', import.meta.url));
let mode = 'outage';
const hits = [];
const server = http.createServer((req, res) => {
  let body = '';
  req.on('data', (c) => (body += c));
  req.on('end', () => {
    hits.push({ method: req.method, url: req.url, cookie: req.headers.cookie || '', body });
    const send = (obj, headers = {}) => { res.writeHead(200, { 'Content-Type': 'application/json', ...headers }); res.end(JSON.stringify(obj)); };
    // Route on the last path segment (the method name), so an overridden path prefix still hits here.
    const method = req.url.split('?')[0].split('/').pop();
    if (method === 'login') {
      if (mode === 'nocookie') return send({ returnCode: '9', returnMsg: 'bad login for s3cretPW' });
      return send({ returnCode: '0' }, { 'Set-Cookie': 'SESSION=abc123; Path=/; HttpOnly' });
    }
    if (method === 'frServiceInfoCheck') {
      if (mode === 'outage') return send({ returnCode: '7070001', returnMsg: 'System error' });
      if (mode === 'area') return send({ returnCode: '1', returnMsg: 'Sorry, the business is out of the service area.' });
      return send({ returnCode: '0', data: { subsInfo: { subsId: 998877, custName: 'SECRET NAME' } } });
    }
    if (method === 'subsShiftingCheckBsnl') return send({ returnCode: '0', data: { shiftingFlag: 'Y' } });
    if (method === 'qryOfferForShifting') return send({ returnCode: '0', data: { offerList: [{ offerId: 176143, offerName: 'FIBRE BASIC', price: 499 }, { offerId: 176147, offerName: 'FIBRE BASIC PLUS', price: 599 }] } });
    res.writeHead(404); res.end('{}');
  });
});

const run = (env, args = ['07242459222']) => new Promise((resolve) => {
  execFile('node', [SCRIPT, ...args], { env: { PATH: process.env.PATH, DSCM_BASE: `http://127.0.0.1:${server.address().port}/portal/drm/api`, ...env } },
    (err, stdout, stderr) => resolve({ code: err ? err.code : 0, out: stdout + stderr }));
});

let bad = 0;
const check = (what, ok, out) => { if (!ok) bad++; console.log(`${ok ? 'PASS' : 'FAIL'} ${what}`); if (!ok) console.log(out); };
const creds = { DSCM_STAFF_CODE: 'staff1', DSCM_STAFF_PWD: 's3cretPW', DSCM_ORG_ID: '307710' };

server.listen(0, '127.0.0.1', async () => {
  let r;
  mode = 'outage'; hits.length = 0;
  r = await run({ DSCM_SESSION: 'given1' });
  check('outage: stops at step 1 with the 7070001 explanation, exit 1', r.code === 1 && /returnCode 7070001 \(BSNL internal/.test(r.out) && /Stopped at step 1/.test(r.out), r.out);
  check('outage: DSCM_SESSION used as the cookie, no login, one call', hits.length === 1 && hits[0].cookie === 'SESSION=given1' && hits[0].url === '/portal/drm/api/ding/frServiceInfoCheck?subsNbr=07242459222', JSON.stringify(hits));

  mode = 'area'; hits.length = 0;
  r = await run({ DSCM_SESSION: 'given1' }, ['0724-2459222']);
  check('out of area: returnCode 1 explained, dash in the number accepted', r.code === 1 && /returnCode 1 \(out of service area/.test(r.out), r.out);

  mode = 'ok'; hits.length = 0;
  r = await run(creds);
  check('full read-only run: login, 3 steps, exit 0', r.code === 0 && /SESSION cookie received/.test(r.out) && /subsId 998877/.test(r.out) && /shiftingFlag Y/.test(r.out) && /2 plan\(s\)/.test(r.out) && /176147  FIBRE BASIC PLUS  599/.test(r.out), r.out);
  check('login body carries the three credentials', JSON.stringify(JSON.parse(hits[0].body)) === JSON.stringify({ staffCode: 'staff1', staffPwd: 's3cretPW', orgId: '307710' }), hits[0].body);
  check('steps 2-3 POST {subsId} with the login cookie', hits.slice(2).every((h) => h.method === 'POST' && h.cookie === 'SESSION=abc123' && h.body === '{"subsId":998877}'), JSON.stringify(hits));
  check('never calls the submit (subsShiftingBsnl)', !hits.some((h) => /subsShiftingBsnl/.test(h.url)), JSON.stringify(hits));
  check('password and customer name never printed', !/s3cretPW|SECRET NAME/.test(r.out), r.out);

  // Paths from a phone capture: host-root-absolute overrides, resolved against the host origin.
  mode = 'ok'; hits.length = 0;
  r = await run({ DSCM_SESSION: 'given1',
    DSCM_STEP1_PATH: '/portal/drm/v2/shift/frServiceInfoCheck',
    DSCM_STEP2_PATH: '/portal/drm/v2/shift/subsShiftingCheckBsnl',
    DSCM_STEP3_PATH: '/portal/drm/v2/shift/qryOfferForShifting' });
  check('overridden host-root paths are used verbatim, run completes', r.code === 0 && /subsId 998877/.test(r.out) && /2 plan\(s\)/.test(r.out), r.out);
  check('… hitting the exact overridden URLs, not BASE+path', hits[0].url === '/portal/drm/v2/shift/frServiceInfoCheck?subsNbr=07242459222' && hits.some((h) => h.url === '/portal/drm/v2/shift/qryOfferForShifting'), JSON.stringify(hits.map((h) => h.url)));

  mode = 'nocookie'; hits.length = 0;
  r = await run(creds);
  check('login without SESSION: stops, password masked in the echoed message', r.code === 1 && /NO SESSION cookie/.test(r.out) && !/s3cretPW/.test(r.out) && /\*\*\*/.test(r.out), r.out);

  r = await run({}, ['12345']);
  check('bad number: usage, exit 1, no request', r.code === 1 && /Usage/.test(r.out), r.out);
  hits.length = 0;
  r = await run({});
  check('no credentials at all: says what to set, no request', r.code === 1 && /Set DSCM_SESSION/.test(r.out) && hits.length === 0, r.out);

  server.close();
  console.log(bad ? `${bad} FAILED` : 'ALL PASS');
  process.exit(bad ? 1 : 0);
});
