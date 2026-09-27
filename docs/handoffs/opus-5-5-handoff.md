# Handoff — FNW FTTH work for Opus 5.5

**Date:** 2026-09-27  
**Branch:** `claude/brave-galileo-ri1g5i` (repo: `fibernetworkworks-droid/FNW_FIN`)  
**Operator:** franchise 307710, Akola, Maharashtra (exchange AKLAKC)

---

## What exists in this repo

All work so far is in `docs/`:

| File | What it contains |
|---|---|
| `docs/reviews/ll-to-ftth-api-comparison.md` | Full comparison of FNW app (CRM-BFM) vs BSNL DSCM API surfaces. §5 has five code-review findings. §6 has the confirmed DSCM copper LL→FTTH flow and current server outage status. |
| `docs/patches/01-moshi-generic-test.md` | Full Kotlin test class to add — guards `FtthJobResponse<T>` Moshi materialization |
| `docs/patches/02-normalize-landline-dedup.md` | Extract `normalizeLandline` to `util/LandlineNumber.kt` + Node `util/landline-number.js` |
| `docs/patches/03-ott-verify-kdoc.md` | KDoc to add at both OTT verify call sites + Retrofit interface |
| `docs/patches/04-lookup-expired-error-code.md` | Add `errorCode:"LOOKUP_EXPIRED"` to VPS response; update app DTO + ViewModel |
| `docs/patches/05-verify-oi26-fixture-branch.md` | Verify/fix `if (oi26)` always-true conditional in live `ftth-service.js` |

---

## The two repos involved

| Repo | Role | Status |
|---|---|---|
| `fibernetworkworks-droid/FNW_FIN` | Documentation repo — you are here | 3 commits ready, push blocked (GitHub App not installed) |
| `fibernetworkworks-droid/fnw-flow-apk` | Android app + VPS backend — where patches 01–05 get applied | Not yet attached to any session |

---

## What needs to happen next

### Task A — Push this repo (blocked)

3 commits on `claude/brave-galileo-ri1g5i` cannot be pushed until an org admin installs the Claude GitHub App:  
`https://github.com/apps/claude/installations/select_target`

Once installed: `git push -u origin claude/brave-galileo-ri1g5i`

### Task B — Apply patches 01–05 to `fnw-flow-apk`

This is the main remaining work. Steps:

1. Attach `fibernetworkworks-droid/fnw-flow-apk` to the session via `add_repo`
2. Clone it locally
3. For each patch spec in `docs/patches/`, read the spec then read the actual source file it targets to confirm field names match
4. Apply the change (new file or edit)
5. Run `./gradlew test` after patches 01–02 to verify tests pass
6. Commit and push each patch on its own branch or a single feature branch

### Patch application order (recommended)

| # | Spec file | Target in `fnw-flow-apk` | Type |
|---|---|---|---|
| 01 | `01-moshi-generic-test.md` | Add `app/src/test/.../FtthJobDeserializationTest.kt` | New test file |
| 02 | `02-normalize-landline-dedup.md` | Add `app/src/main/.../util/LandlineNumber.kt`; edit `FtthConversionViewModel.kt`; add `tools/ftth/util/landline-number.js` | Refactor |
| 03 | `03-ott-verify-kdoc.md` | Edit `FtthConversionViewModel.kt` + `FNWFlowApi.kt` | KDoc only |
| 04 | `04-lookup-expired-error-code.md` | Edit `tools/ftth/ftth-service.js` (VPS) + `FtthV3Dtos.kt` + `FtthConversionViewModel.kt` | Cross-layer |
| 05 | `05-verify-oi26-fixture-branch.md` | Read `tools/ftth/fixtures/ftth-service.js` and `tools/ftth/ftth-service.js` first — verification before edit | Verify then fix |

---

## Key source files in `fnw-flow-apk` (paths confirmed from earlier read)

```
app/src/main/kotlin/com/fnw/flow/ftth/
    FtthConversionViewModel.kt      — main ViewModel; has normalizeLandline, lookup-expired match, OTT verify calls
    FtthConversionRepository.kt     — pollJob(), LOST_TRACK branch
    FtthV3Dtos.kt                   — DTOs incl FtthJobResponse<T>, FtthJob<T>, error response
    FNWFlowApi.kt                   — Retrofit interface; v1OttVerify, v3OtpVerify declarations

app/src/test/kotlin/com/fnw/flow/ftth/
    (FtthJobDeserializationTest.kt does not exist yet — patch 01 creates it)

tools/ftth/
    ftth-service.js                 — live VPS handler
    fixtures/ftth-service.js        — fixture with if (oi26) constant
    util/                           — (landline-number.js does not exist yet — patch 02 creates it)

tools/patch-ftth-robust.py          — anchor-based patch script referenced in patch 05
```

---

## DSCM API context (no credentials — read-only reference)

**Gateway:** `https://wsc.cdr.bsnl.co.in/portal/drm/api`  
**Auth:** SESSION cookie obtained from `/portal/drm/api/login` using `staffCode`/`staffPwd`/`orgId`

**Confirmed copper LL→FTTH flow (DSCM Shift):**
```
GET  ding/frServiceInfoCheck?subsNbr=<landline>    →  subsId   [ENTRY POINT — currently returning 7070001 server-side outage]
POST ding/subsShiftingCheckBsnl   {subsId}          →  shiftingFlag Y/N
POST ding/qryOfferForShifting     {subsId}          →  plan list
POST ding/subsShiftingBsnl        {subsId, planId}  →  submit
```

**Current status:** `frServiceInfoCheck` returns `7070001` (BSNL internal error) for all numbers including known active FTTH subscribers. This is a BSNL server-side outage — not a credentials or territory issue. No action possible until BSNL restores the endpoint.

**Error codes reference:**
```
returnCode "0"        success
returnCode "1"        out of service area (line not bound to this franchise)
returnCode "7070001"  BSNL internal/unknown error (current outage code)
42001044              not in franchise / SPI downstream failure
41600024              required parameter null
```

---

## What NOT to do

- Do not make live BSNL API calls from Claude's cloud container — the auto-mode classifier blocks outbound calls to `wsc.cdr.bsnl.co.in`. All curl testing must be run from the operator's own VPS.
- Do not paste SESSION cookies or passwords inline in chat — commit credentials-free context to files instead.
- Do not apply patch 05 without reading `ftth-service.js` first — it is a verification task before an edit.
