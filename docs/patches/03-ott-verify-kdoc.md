# Patch 03 — KDoc on OTT verify call sites (Quick vs Guided semantics)

**Finding:** The two OTT verify calls have opposite semantics and that difference is nowhere
documented at the call sites:

| Call | What it does |
|---|---|
| Quick: `v1OttVerify` | Sends OTP to BSNL **and finalizes the order** in a single call. |
| Guided: `v3/otp/verify` | **Format-check + stash only** — stores the OTP code; the actual BSNL verify and order finalization happen later inside `v3/submit`. |

A developer reading either call site in isolation cannot tell which mode they're in, making it easy
to add retry logic or error handling that is correct for one mode but wrong for the other.

**File to change in `fnw-flow-apk`:**
- `app/src/main/kotlin/com/fnw/flow/ftth/FtthConversionViewModel.kt`

---

## Locate the two call sites

Search for the verify calls:
```
grep -n "v1OttVerify\|v3/otp/verify\|ottVerify\|otpVerify" app/src/main/kotlin/com/fnw/flow/ftth/FtthConversionViewModel.kt
```

You will find two blocks, one in the quick-mode flow (`quickDoConvert` or similar) and one in the
guided-mode flow (`guidedDoSubmit` or similar).

---

## Quick-mode verify — add KDoc before the call

```kotlin
// BEFORE
val verifyResult = repository.v1OttVerify(number, otpCode, resumeKey)

// AFTER
/**
 * QUICK MODE — finalizes the order.
 * This single call sends the OTP to BSNL AND completes the conversion.
 * On success the order is done; on failure it is not recoverable without a new lookup.
 * Do NOT add a "verify succeeded → now submit" step here; there is no separate submit in V1.
 */
val verifyResult = repository.v1OttVerify(number, otpCode, resumeKey)
```

## Guided-mode verify — add KDoc before the call

```kotlin
// BEFORE
val verifyResult = repository.v3OtpVerify(number, otpCode, resumeKey)

// AFTER
/**
 * GUIDED MODE — stash only, NOT a finalization.
 * This call validates OTP format and stores the code server-side.
 * The actual BSNL OTP verification and order submission happen together in v3/submit.
 * Retrying on failure here is safe; retrying after v3/submit is NOT (PONR risk).
 */
val verifyResult = repository.v3OtpVerify(number, otpCode, resumeKey)
```

## Also annotate the Retrofit interface declarations

In `FNWFlowApi.kt`, locate the two `@POST` declarations and add a one-liner above each:

```kotlin
/** Quick mode: verifies OTP AND finalizes the order. Single-call finalization. */
@POST("api/ftth/convert/ott/verify")
suspend fun v1OttVerify(@Body req: V1OttVerifyRequest): V1OttVerifyResponse

/** Guided mode: stash-only. Real BSNL verify happens inside v3/submit. */
@POST("api/ftth/v3/otp/verify")
suspend fun v3OtpVerify(@Body req: V3OtpVerifyRequest): V3OtpVerifyResponse
```

These annotations make the asymmetry visible to anyone reading the interface, not just the ViewModel.
