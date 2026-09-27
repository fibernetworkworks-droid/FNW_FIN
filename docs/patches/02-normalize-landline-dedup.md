# Patch 02 — De-duplicate `normalizeLandline`

**Finding:** `normalizeLandline` appears in `FtthConversionViewModel.kt` companion object with the
comment "same regex as v1Convert validator", implying a second copy exists on the VPS backend
(`ftth-service.js` or similar). Two copies will drift — one accepting edge cases the other rejects.

**Files to change in `fnw-flow-apk`:**
- Add: `app/src/main/kotlin/com/fnw/flow/util/LandlineNumber.kt`
- Modify: `app/src/main/kotlin/com/fnw/flow/ftth/FtthConversionViewModel.kt`

---

## Step 1 — New utility object

```kotlin
// app/src/main/kotlin/com/fnw/flow/util/LandlineNumber.kt
package com.fnw.flow.util

object LandlineNumber {
    // STD+number: strip spaces, dashes, leading zeros from the area code.
    // Examples: "0724-2459222" → "07242459222", "0724 245 9222" → "07242459222"
    private val NORMALIZE_REGEX = Regex("[\\s\\-]")

    fun normalize(raw: String): String = raw.replace(NORMALIZE_REGEX, "")

    /** Returns true when the normalized form looks like a 10- or 11-digit Indian landline. */
    fun isValid(raw: String): Boolean {
        val n = normalize(raw)
        return n.matches(Regex("0[0-9]{9,10}"))
    }
}
```

> Adjust the regex to match whatever `normalizeLandline` in the ViewModel currently does — the goal
> is a single canonical definition, not rewriting the logic.

## Step 2 — Replace the ViewModel companion copy

Locate in `FtthConversionViewModel.kt`:

```kotlin
// BEFORE (companion object, roughly)
companion object {
    // same regex as v1Convert validator
    fun normalizeLandline(raw: String): String =
        raw.replace(Regex("[\\s\\-]"), "")
    // ...
}
```

Replace with a delegation:

```kotlin
// AFTER
companion object {
    fun normalizeLandline(raw: String): String = LandlineNumber.normalize(raw)
    // ...
}
```

All existing call sites `normalizeLandline(x)` continue to compile unchanged; the companion wrapper
keeps the public surface stable for now and can be removed in a follow-up once callers are migrated.

## Step 3 — Backend copy (VPS / Node.js)

On the VPS side, locate the `"same regex as v1Convert validator"` comment in `ftth-service.js` (or
whichever file it's in). Extract it to a shared module:

```js
// tools/ftth/util/landline-number.js
const NORMALIZE = /[\s\-]/g;

function normalize(raw) {
    return String(raw).replace(NORMALIZE, '');
}

function isValid(raw) {
    return /^0[0-9]{9,10}$/.test(normalize(raw));
}

module.exports = { normalize, isValid };
```

Then in the files that had the inline copy:

```js
// BEFORE
const num = raw.replace(/[\s\-]/g, '');

// AFTER
const { normalize } = require('./util/landline-number');
const num = normalize(raw);
```

Run the existing test suite (or a quick manual smoke test) after the replacement.
