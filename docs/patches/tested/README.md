# Patches 01–05, tested but NOT applied to fnw-flow-apk

These five `git am` files are the specs in `docs/patches/` turned into code for
`fibernetworkworks-droid/fnw-flow-apk` and tested in a throwaway copy of that repo. Nothing was
committed or pushed to fnw-flow-apk.

- **Base:** fnw-flow-apk `main` at `872dc5f` (27 Sep 2026).
- **Applies cleanly:** `git am docs/patches/tested/*.patch` (12 files, +188 / −21).

## Test results (27 Sep 2026)

| Check | Result |
|---|---|
| `./gradlew :app:testReleaseUnitTest` (what the Android Branch Check CI runs) | **162 tests, 22 classes, 0 failures** |
| `node tools/ftth-robust-test.mjs` (patch script + ftth-jobs.js against a mock BSNL) | **PASS**, including the new `errorCode` check |
| Mutation check: undo the patch 02 and 04 fixes, run their new tests | Both new tests **fail** as they should; the old wording-based test still passes |

All tests use mock servers. No BSNL, DSCM or FNW server was called.

## What each patch does, and where the specs were wrong

Paths in the specs (`app/src/main/kotlin/com/fnw/flow/ftth/...`) don't exist. The real code is under
`app/src/main/java/com/fnw/flow/operator/...`. Each patch was written against the real files.

| # | Change | Differences from the spec |
|---|---|---|
| 01 | `data/api/dto/FtthJobDeserializationTest.kt`: 3 tests that the job route's `result` decodes as `V1ConvertResponse` / `V3SubmitResponse`, using the app's own `NetworkModule.provideMoshi()`. | Real field names (`orderNumber`, `bbUserId`, `success`, …). The tests pass, so the Moshi wiring was already correct: this is a guard, not a fix. |
| 02 | `util/LandlineNumber.kt` holds the normalizer; the ViewModel delegates to it; `LandlineNumberTest` pins the accepted formats. | Keeps the real logic (digits only, returns `null` when invalid), not the spec's regex. **Fixes a bug:** `091…` numbers normalized to 12 digits (`917242459222`). There is no backend copy in the repo, so the spec's Node `landline-number.js` was not added. |
| 03 | KDoc on `v1OttVerify`, `v1OttVerifyStart` and `v3OtpVerify` in `FNWFlowApi.kt`, plus one line on each ViewModel function contrasting Quick and Guided. | The repository, DTOs and ViewModel already documented the difference; only the Retrofit declarations lacked it. |
| 04 | `tools/ftth/ftth-jobs.js` sends `errorCode: 'LOOKUP_EXPIRED'` with its "Lookup expired" 400. The app carries `code` on `ConvertException` and refreshes the lookup on the code, keeping the text match for older servers. | The message comes from `ftth-jobs.js` `startQuickConvert`, not `ftth-service.js`. The old synchronous `/api/ftth/convert` route is in the live `server.js`, which is not in the repo, so it still relies on the text fallback. |
| 05 | Two-line comment in both fixtures: the `oi26` guard is a stand-in. | **The spec's risk can't happen.** `patch-ftth-robust.py` anchors only on the `voiceSupp` table and inserts after it; it never copies fixture code into the live file. To see the live guard, run on the VPS: `grep -n "oi26" automation/ftth-service.js automation/ftth-ott.js`. |

## To apply later

1. `git am` the five files on a branch of fnw-flow-apk.
2. Deploy `ftth-jobs.js` to the VPS and release the app in either order: the error text is
   unchanged, and the app keeps the text match.
3. Remove the text fallback in the ViewModel once every server sends `errorCode`.
