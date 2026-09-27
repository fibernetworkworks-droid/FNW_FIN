# Patch 05 — Verify `if (oi26)` fixture branch vs live `ftth-service.js`

**Finding:** In `tools/ftth/fixtures/ftth-service.js`:

```js
const oi26 = 26;
// ...
if (oi26) {
    // voice service block
}
```

`if (oi26)` is always `true` — `26` is truthy. This is correct for the fixture (it's a constant
placeholder). **The risk** is that `patch-ftth-robust.py` uses anchor-based patching to splice code
into the live `ftth-service.js` from this fixture. If the live file once had a real conditional
(e.g. `if (orderInfo.includeVoice)`) in the same position, and the patch replaced it with the
fixture's always-true version, voice services are now unconditionally forced into every FTTH order —
including ones where the subscriber doesn't have voice.

This is a **verification task**, not a guaranteed bug. The question is: does the live file have the
same always-true form, or is there a real conditional?

---

## Verification steps (run on the VPS)

### 1. Grep the live file for `oi26`

```bash
grep -n "oi26" /path/to/tools/ftth/ftth-service.js
```

Expected outputs:
- **Not found** → the fixture constant was inlined by value, not by name. Look for `if (26)` instead.
- **Found, same form (`const oi26 = 26`)** → the fixture was spliced in as-is; confirm this is intentional.
- **Found, different form** → investigate what `oi26` means in the live file.

### 2. Grep for the surrounding voice-service block

```bash
grep -n "voiceSupp\|voice_supp\|includeVoice\|addVoice\|CALL_FORWARD\|START_ORDER_FLOW" \
    /path/to/tools/ftth/ftth-service.js | head -40
```

Look for whether the block that was patched in is guarded by a real condition or is unconditional.

### 3. Check what `patch-ftth-robust.py` inserts at the anchor

In `tools/patch-ftth-robust.py`, find the anchor for the voice-service insertion:

```bash
grep -n "anchor\|START_ORDER_FLOW\|oi26\|voiceSupp" tools/patch-ftth-robust.py
```

Read the patch block it inserts. If it includes `if (oi26)` verbatim, the live file will have the
same always-true conditional after patching.

---

## If the live conditional is wrong

If the live `ftth-service.js` has `if (oi26)` (always-true) where it should have a real check,
the fix is:

```js
// BEFORE (from fixture, always-true)
const oi26 = 26;
if (oi26) {
    // voice service block applied to every order
}

// AFTER (use the real flag from orderInfo / request payload)
if (orderInfo.addVoiceServices !== false) {
    // voice service block applied only when voice is requested
}
```

The exact condition depends on what field the app sends to signal voice inclusion — check
`V1ConvertRequest.addClipManually` and `V3SubmitRequest` in the Kotlin DTOs for the relevant field,
then find where the VPS reads it.

---

## If the fixture is intentionally always-true

If BSNL always requires voice services to be set during an FTTH conversion (i.e. there is no
voice-optional path), then `if (oi26)` as an always-true anchor is fine — but the constant should
be renamed to make the intent clear:

```js
// BEFORE
const oi26 = 26;
if (oi26) { ... }

// AFTER — rename so it's obviously intentional
const ALWAYS_INCLUDE_VOICE = true;  // BSNL requires voice config in every FTTH order
if (ALWAYS_INCLUDE_VOICE) { ... }
```

This removes the confusion for anyone who reads the code later.
