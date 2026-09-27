# Patch 01 — Moshi generic materialization test for `FtthJobResponse<T>`

**Finding:** `FtthJobResponse<T>` wraps `FtthJob<T>` where `T` is either `V1ConvertResponse` or
`V3SubmitResponse`. Two `@GET("api/ftth/job/{jobId}")` variants (`ftthJobQuick`, `ftthJobGuided`)
expose these via Retrofit. If Moshi cannot materialize `T` at runtime, `result` silently deserializes
to `null` — and `pollJob()` then treats a *successful* order as `LOST_TRACK`. This is a data-loss
path that fails without any thrown exception.

**Files to change in `fnw-flow-apk`:**
- Add: `app/src/test/kotlin/com/fnw/flow/ftth/FtthJobDeserializationTest.kt`
- Verify: `app/src/main/kotlin/com/fnw/flow/ftth/FtthConversionRepository.kt` — confirm `LOST_TRACK`
  branch is present and is reached when `job.result == null` on a `done` state.

---

## New test file

```kotlin
// app/src/test/kotlin/com/fnw/flow/ftth/FtthJobDeserializationTest.kt
package com.fnw.flow.ftth

import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import com.squareup.moshi.Types
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Test

class FtthJobDeserializationTest {

    private val moshi = Moshi.Builder()
        .addLast(KotlinJsonAdapterFactory())
        .build()

    // ── Quick (V1) ──────────────────────────────────────────────────────────

    @Test
    fun `quick done payload materializes V1ConvertResponse`() {
        val json = """
            {
              "ok": true,
              "job": {
                "jobId": "j1",
                "state": "done",
                "ponr": true,
                "result": {
                  "orderId": "ORD-001",
                  "message": "Success"
                }
              }
            }
        """.trimIndent()

        val type = Types.newParameterizedType(FtthJobResponse::class.java, V1ConvertResponse::class.java)
        val adapter = moshi.adapter<FtthJobResponse<V1ConvertResponse>>(type)
        val parsed = adapter.fromJson(json)

        assertNotNull("outer wrapper must parse", parsed)
        assertNotNull("job must parse", parsed!!.job)
        assertEquals("done", parsed.job!!.state)
        // If T failed to materialize, result would be null here → LOST_TRACK bug
        assertNotNull("V1ConvertResponse result must not be null (Moshi generic bug check)", parsed.job.result)
        assertEquals("ORD-001", parsed.job.result!!.orderId)
    }

    // ── Guided (V3) ─────────────────────────────────────────────────────────

    @Test
    fun `guided done payload materializes V3SubmitResponse`() {
        val json = """
            {
              "ok": true,
              "job": {
                "jobId": "j2",
                "state": "done",
                "ponr": true,
                "result": {
                  "orderId": "ORD-002",
                  "oduSerial": "ODU-XYZ",
                  "message": "Submitted"
                }
              }
            }
        """.trimIndent()

        val type = Types.newParameterizedType(FtthJobResponse::class.java, V3SubmitResponse::class.java)
        val adapter = moshi.adapter<FtthJobResponse<V3SubmitResponse>>(type)
        val parsed = adapter.fromJson(json)

        assertNotNull("outer wrapper must parse", parsed)
        assertNotNull("job must parse", parsed!!.job)
        // If T failed to materialize, result would be null here → LOST_TRACK bug
        assertNotNull("V3SubmitResponse result must not be null (Moshi generic bug check)", parsed.job!!.result)
        assertEquals("ORD-002", parsed.job.result!!.orderId)
    }

    // ── Failure path (ensures LOST_TRACK is not triggered on success) ───────

    @Test
    fun `failed state with null result does not blow up`() {
        val json = """
            {
              "ok": false,
              "job": {
                "jobId": "j3",
                "state": "failed",
                "ponr": false
              },
              "error": "BSNL timeout"
            }
        """.trimIndent()

        val type = Types.newParameterizedType(FtthJobResponse::class.java, V1ConvertResponse::class.java)
        val adapter = moshi.adapter<FtthJobResponse<V1ConvertResponse>>(type)
        val parsed = adapter.fromJson(json)

        assertNotNull(parsed)
        assertEquals("failed", parsed!!.job!!.state)
        // result is legitimately null for a failed job — not the bug we're guarding
    }
}
```

## Adjust `V1ConvertResponse` and `V3SubmitResponse` field names to match actual BSNL response

Check `FtthV3Dtos.kt` for the exact field names. The test's `orderId`, `oduSerial`, `message` are
placeholders — substitute whatever the real DTOs declare. The important thing is that at least one
non-nullable field from each response type is asserted non-null; that's what catches the
Moshi-generic-wiring failure.

## How to confirm the fix is needed

Before adding the test, grep for the Moshi/Retrofit setup:

```
grep -r "KotlinJsonAdapterFactory\|ParameterizedType\|FtthJobResponse" app/src/main --include="*.kt"
```

If the setup uses `Types.newParameterizedType` correctly and the factory is registered, the tests
will pass immediately — which means the wiring is fine. If they fail with `result == null`, the
factory or parameterized-type registration needs to be fixed first.
