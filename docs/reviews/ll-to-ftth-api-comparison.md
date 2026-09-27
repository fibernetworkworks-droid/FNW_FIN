# LL/BB → FTTH: two BSNL surfaces compared

**Reviewer:** Claude Code · **Date:** 2026-09-27
**Sources:**
- `fnw-flow-apk` (branch `claude/funny-sagan-63j31a`, commit `a1f1d0c`) — the FNW operator app plus its VPS backend
- The BSNL DSCM API handoff (endpoints under `/portal/drm/api/ding/...` used by the `com.bsnl.dscm` franchisee app)

This document records what each surface does, where they map to each other, and where they don't. It is a code review artifact — no live production calls were made against either.

---

## 1. Headline

The FNW app and the DSCM API notes reach the same business outcome (copper LL/BB → FTTH conversion for a BSNL franchisee) through **two entirely different BSNL surfaces**. They share almost no endpoints.

| | **FNW app (`fnw-flow-apk`)** | **DSCM franchisee API (handoff)** |
|---|---|---|
| BSNL surface | CRM web portal — `/portal/crm/callservice.json`, `CallCrmDubboService` | DSCM mobile API — `/portal/drm/api/ding/...` |
| Auth | CRM web login + CSRF (`web-session.js`, `dscmUsername`/`dscmPassword`) | `SESSION` cookie + `userId`/`orgId`/`areaId` |
| Order mechanism | Drives BSNL's **BFM order-flow wizard** (`START_ORDER_FLOW` → `BO_CHANGE` → `NEXT_FLOW_STEP` → `SuccessPage`) | Purpose-built JSON request/response per step |
| Modeled as | `CheckCanStartFlow`, `subsEventId: 35` — "Service Conversion" (in-place main-product change) | Three distinct flows: **Shift**, **changeMainProd**, and **`lltoftth` cluster** |
| Weight per order | ~150 BSNL calls, 25–60s | A handful of JSON calls per step |

So the app **does not call any `/ding/...` endpoint** from the handoff. It reproduces the conversion by scripting the human CRM order wizard instead.

---

## 2. Step-by-step endpoint mapping

| FNW app step (endpoint) | What it does at BSNL | Nearest DSCM-API equivalent |
|---|---|---|
| `POST /api/ftth/lookup`, `POST /api/ftth/v3/lookup` | `qrySubsPageTree` + `selectConvertible()` | `qryCustListBsnl` → `qrySubsListBsnl` → `qrySubsDetailBsnl` |
| eligibility gate (inline in lookup) | `CheckCanStartFlow` (event 35) | `subsShiftingCheckBsnl` / `changeMainProdCheckBsnl` |
| plan list (`availablePlans`, server-side `PLAN_MAP`) | plans folded into the lookup response | `qryOfferForShifting` / `qryAvailablePlanListBsnl` |
| `POST /api/ftth/v3/configure` | BFM `BO_CHANGE` on voice services, CLIP, wifi roaming | *(no equivalent — DSCM folds config into the submit body)* |
| `POST /api/ftth/convert`, `POST /api/ftth/v3/submit` | BFM `NEXT_FLOW_STEP` → expects `wizardPage.code === 'SuccessPage'` | `subsShiftingBsnl` / `changeMainProdBsnl` (single call) |
| `POST /api/ftth/convert/ott` + `/ott/verify` | `OtpNotifySerivce` P1→P3, then verify | *(handoff documents no OTT/OTP endpoint)* |
| — | — | **`lltoftth/qryClusterByCondition` → `qryGroupByClusterId` → `updateFlagByFranchise`** — no FNW app equivalent |
| `POST /api/ftth/{convert,ott/verify,v3/submit}/start` + `GET /api/ftth/job/:jobId` | FNW backend background-job wrapper (per-number Redis lock) | *(no analogue — DSCM calls are synchronous)* |

---

## 3. Two divergences that matter

### 3.1 The FNW app has no `lltoftth` cluster flow

The DSCM API shows BSNL exposes a dedicated LL→FTTH cluster-migration namespace: `qryClusterByCondition` → `qryGroupByClusterId` → `updateFlagByFranchise` (accept/reject per franchise). The FNW app ignores it entirely and instead does an individual BFM "Service Conversion (event 35)."

**Open question for BSNL operations:** does an app-driven event-35 conversion get counted the same as an `lltoftth` cluster migration for commissioning, quota, and records? If BSNL's official copper→FTTH program is the cluster one, FNW conversions may sit in a different bucket than BSNL expects. Worth clarifying with BSNL directly — no amount of code reading tells us how the back-office reconciles these.

### 3.2 "Service Conversion" vs "Shift" vs "changeMainProd"

Event 35 (what FNW does) is closest to **`changeMainProdBsnl`** — an in-place main-product change — not `subsShiftingBsnl`, which is a physical shift. The BSNL handoff was on the shift + `frServiceInfoCheck` path. These are different BSNL order types with different eligibility rules and outputs, so a 1:1 comparison of behaviour won't hold across them.

---

## 4. What each side does better

### 4.1 The FNW backend is production-hardened well beyond a raw DSCM client

- **Background jobs + per-number Redis lock** (`automation/ftth-jobs.js`). Directly fixes the "one number converted 4× in 2 minutes" incident on 24 Sep 2026.
- **Explicit `PONR` / `uncertain` / `submitted` states** so a slow BSNL confirm doesn't trigger a blind retry.
- **Duplicate-voice-service recovery** (`duplicateVoiceService` + `rememberKeepVoice`): when BSNL refuses "Not allow to duplicate order the CALL_FORWARDING" at preview, the order is redone with that service kept as existing (`X`), and the choice is remembered per number for 30 days.
- **Multi-tenant isolation**: jobs and resume-keys namespaced by `masterId`; cross-master resume attempts rejected with 403.
- **OTP hygiene**: `otpCode` and `resumeKey` explicitly stripped before tool logging.
- **Idempotent, self-checking patch scripts** (`patch-ftth-active-sub.py`, `patch-ftth-robust.py`): back files up, run `node --check`, revert all-or-nothing on syntax failure.
- **`selectConvertible()` prefers ACTIVE rows** — fixes a Goa case where BSNL returned a live line's number alongside a disconnected earlier row and the dead row won the pick.

### 4.2 The DSCM API would be lighter — with caveats

Structured JSON, fewer calls per order, no dependency on wizard step names like `SuccessPage` (which BSNL could rename in a portal release). But — it is undocumented and reverse-engineered from the APK. Migrating a production flow onto it trades the hard-won resilience layer above for something BSNL can change silently. Not a decision to drift into.

---

## 5. Code-review findings from the full read

Ordered rough severity ↓.

1. **Moshi generic wiring — verify or add a test.**
   `FtthJobResponse<T>` wraps `FtthJob<T>` where `T` is either `V1ConvertResponse` or `V3SubmitResponse`. Retrofit exposes this via two `@GET("api/ftth/job/{jobId}")` variants (`ftthJobQuick`, `ftthJobGuided`). If the Moshi converter can't materialize `T` at runtime, `result` deserializes to `null` and `pollJob()` treats a *successful* order as `LOST_TRACK`. Add a targeted test that decodes a real "done" payload for each variant end-to-end.

2. **`normalizeLandline` is duplicated.**
   Once in the ViewModel companion, and the comment says "same regex as v1Convert validator" — implying a second copy on the backend too. Two copies will drift. Move to a single `util.LandlineNumber.normalize()` and have both call it.

3. **OTT verify semantics differ between modes.**
   Quick `v1OttVerify` *finalizes*. Guided `v3/otp/verify` is only "format check + stash" — the real BSNL verify runs inside `v3/submit`. This is deliberate but a foot-gun. Add a KDoc at each verify call site making the difference explicit.

4. **Lookup-cache coupling is prose-matched.**
   Quick convert depends on the 600s `ftth-lookup:` cache. When it's gone, the ViewModel matches the server error string `"lookup expired"` by substring to trigger auto-refresh. If that message is ever reworded, the auto-refresh silently stops working. Return a structured error code (`"LOOKUP_EXPIRED"`) instead.

5. **Fixture `if (oi26)` masks the real branch.**
   `const oi26 = 26; if (oi26)` in the fixtures is always-true. Fine as a fixture, but confirm the anchor-based patch scripts aren't papering over a real conditional in the live `ftth-service.js` that has different behaviour when it's false.

---

## 6. On `0724-2459222` (Akola)

The DSCM handoff flagged this as a blocker. It isn't a code problem.

- `frServiceInfoCheck?subsNbr=07242459222` returned `{"returnCode":"1","returnMsg":"Sorry, the business is out of the service area."}`.
- In franchisee terms this means: **the line exists at BSNL but is not bound to franchise 307710** (Akola FIBER NE07710, exchange `AKLAKC`). It's in another franchise's territory.
- The FNW app's own gate would reach the same conclusion via a different route — `CheckCanStartFlow` would either fail or the line wouldn't appear in this franchise's `qrySubsPageTree`.
- Neither integration path — CRM-BFM or DSCM — legitimately converts a subscriber outside the operator's franchise.
- If the customer wants FTTH: the request goes through whichever franchise the line is bound to. If FNW believes the mapping is wrong (the line physically sits in Akola but is administratively mapped elsewhere), that's a territory-correction request to raise with BSNL's franchisee support, referencing `subsNbr 07242459222`, exchange `AKLAKC`, franchise `307710`, and `returnCode:"1"`.

---

## 7. Recommendation

Keep the CRM-web-session path as the production engine. It's the sanctioned surface, and the resilience layer around it is the part you don't want to throw away. Before considering any move onto `/ding/...`:

1. Confirm with BSNL that event-35 conversions and the `lltoftth` cluster program are equivalent for commissioning and records.
2. Weigh the durability trade-off: DSCM is undocumented and can break without notice.

For this repo (`FNW_FIN`), the natural next steps are the three actionable findings in §5.1–§5.3 — they don't touch the CRM contract and pay off immediately.
