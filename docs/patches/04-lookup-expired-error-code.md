# Patch 04 — Replace `"lookup expired"` prose match with structured error code

**Finding:** In `FtthConversionViewModel.kt`, the quick-convert flow triggers an auto-refresh when it
receives a server error. It detects this by substring-matching the error string `"lookup expired"`.
If that message is ever reworded (e.g. in a VPS deploy), the auto-refresh silently stops working —
the user sees a generic error instead of the lookup being re-fetched.

**Files to change:**
- VPS: `tools/ftth/ftth-service.js` (or whichever handler returns this error)
- App: `app/src/main/kotlin/com/fnw/flow/ftth/FtthConversionViewModel.kt`
- App: `app/src/main/kotlin/com/fnw/flow/ftth/FtthV3Dtos.kt` (or wherever the error response DTO lives)

---

## Step 1 — VPS: return a structured error code

Locate the place in `ftth-service.js` (or `server.js`) that returns the lookup-expired response.
It currently sends something like:

```js
// BEFORE
return res.json({ ok: false, error: 'lookup expired' });
```

Replace with a structured body that includes a machine-readable code:

```js
// AFTER
return res.json({ ok: false, error: 'lookup expired', errorCode: 'LOOKUP_EXPIRED' });
```

`error` is kept for backwards compatibility with any older app versions still in the field.

## Step 2 — App DTO: add `errorCode` field

In the error/response DTO (likely `FtthV3Dtos.kt` or a generic `ApiError`):

```kotlin
// BEFORE
data class FtthErrorResponse(
    val ok: Boolean,
    val error: String? = null
)

// AFTER
data class FtthErrorResponse(
    val ok: Boolean,
    val error: String? = null,
    val errorCode: String? = null   // machine-readable; "LOOKUP_EXPIRED", etc.
)
```

## Step 3 — App ViewModel: switch from substring to code check

Locate the prose match in `FtthConversionViewModel.kt`:

```kotlin
// BEFORE
if (e.message?.contains("lookup expired", ignoreCase = true) == true) {
    // trigger auto-refresh
    autoRefreshLookup()
}
```

Replace with a code check, with the prose match as a fallback for any already-deployed VPS versions
that don't yet return `errorCode`:

```kotlin
// AFTER
val isLookupExpired = (e as? FtthApiException)?.errorCode == "LOOKUP_EXPIRED"
    || e.message?.contains("lookup expired", ignoreCase = true) == true
if (isLookupExpired) {
    autoRefreshLookup()
}
```

Once all VPS instances are deployed with `errorCode`, the prose fallback can be removed.

---

## Why the fallback matters

There is a window between when the app update ships and when the VPS is updated (or vice versa).
The fallback keeps both directions of that window working. Deploy VPS first, then the app update;
remove the prose fallback in the next app release.
