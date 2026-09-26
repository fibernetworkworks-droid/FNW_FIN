# Zee5 Live Server Probe — API Access Report
**App:** `com.graymatrix.did` (Zee5) v39.61.8  
**Probed:** 2026-09-26  
**Method:** Unauthenticated (platform token only, no user account)

---

## Executive Summary

The Zee5 GraphQL API at `artemis.zee5.com/artemis/graphql` is accessible using only a platform-level JWT token, obtainable without any credentials. Video URL paths for all content (movies, episodes) are exposed in API responses and the CDN delivers HLS/DASH manifests and TS segments without authentication. **However, every piece of video content — including content labelled "free/AVOD" — is protected by SAMPLE-AES (HLS) and Widevine + PlayReady (DASH) DRM.** Decryption requires a license from the key server, which in turn requires an authenticated user session.

---

## 1. Authentication — Platform Token

**Endpoint:** `GET https://launchapi.zee5.com/launch?platform_name=android_app`  
**Auth required:** None  
**Response field:** `platform_token.token`

The token is an HS256 JWT signed with a server-side secret. Decoded payload:
```json
{
  "platform_code": "@ndroid@pp@123",
  "issuedAt": "2026-09-26T16:48:59.005Z",
  "product_code": "zee5@975",
  "ttl": 86400000
}
```

TTL is 86,400,000 ms (24 hours). This token grants access to all public GraphQL queries and is the only credential needed to reach browse and content-metadata APIs.

---

## 2. GraphQL API Access

**Endpoint:** `POST https://artemis.zee5.com/artemis/graphql`  
**Header:** `x-access-token: <platform_token>`

### 2a. Homepage Navigation
```graphql
{ collection(id: "0-8-homepage") { id title rails { id title } } }
```

Live rails returned (sample):
| Rail ID | Title |
|---------|-------|
| `0-8-manualcol_1053401488` | SVOD - Main HP Banner |
| `0-8-3z5194652` | Trending Near You |
| `0-8-3z5812688` | Mass Entertainers |
| `0-8-6818` | Free Malayalam TV Shows |
| `0-8-3z5984645` | Must-Watch Movies |
| `0-8-3z51032427` | What India is Watching |

### 2b. Movie Video URLs (tvShowRelatedContent query)

**Query:**
```graphql
{ tvShowRelatedContent(id: "<movie_id>", country: "IN", translation: "en") {
    id title billingType assetSubType
    video { hlsUrl url isDrm drmKey }
} }
```

Live results:

| Movie | ID | HLS Path | DASH Path | isDrm | DRM Key |
|-------|----|----------|-----------|-------|---------|
| Kaatera | `0-0-1z5508837` | `/drm1/titanfile/hls/MOVIES/V2PRIME/4K/ATMOS/KAATERA/…/index.m3u8` | `/drm1/titanfile/dash/…/manifest.mpd` | true | `9691a904-b5b2-320c-8bb6-d6addc8c56fa` |
| Head Bush | `0-0-1z5285324` | `/drm1/elemental/hls/MOVIES/V2PRIME/4K/ATMOS/HEAD_BUSH/…/index.m3u8` | `/drm1/elemental/dash/…/manifest.mpd` | true | (Widevine) |
| Vedha | `0-0-1z5294923` | `/drm1/elemental/hls/MOVIES/V2PRIME/MULTI_AUDIO/DDPLUS/VEDHA/…/index.m3u8` | — | true | — |
| Karz | `0-0-movie_1633188359` | `/drm/PRIORITY1080/HINDI_MOVIES/Karz_Hindi_Movie.mp4/index.m3u8` | — | true | — |
| Anjaam | `0-0-movie_1430588912` | `/drm1/elemental/hls/Movies/Drama/Anjaam_Hindi_Movie_RTR_…/index.m3u8` | — | true | — |
| Purab Aur Pashchim | `0-0-2525` | `/drm/PRIORITY720/HINDI_MOVIES/Purab_Aur_Pachhim_Hindi_Movie.mp4/index.m3u8` | `/drm/PRIORITY720/…/manifest.mpd` | true | `eb914881-d237-46c6-b5d0-f664235f2d48` |
| Shirdi Ke Sai Baba | `0-0-2534` | `/drm/720p/movies/Hindi_Movies/Shridi_Ke_Sai_Baba_Hindi_Movie.mp4/index.m3u8` | `/drm/720p/…/manifest.mpd` | true | `eb914881-d237-46c6-b5d0-f664235f2d48` |

**CDN base:** `https://mediacloudfront.zee5.com` (all paths above are relative to this).

### 2c. TV Episode Video URLs (GetEpisodes query)

**Query:**
```graphql
{ episodes(filter: { itemType: episode, seasonId: "0-2-5z51079672", country: "IN", page: 0, limit: 5 }) {
    contents { ... on Episode { id title billingType tier video { url hlsUrl isDrm drmKey } } }
} }
```

Live example (SaReGaMaPa 2026):
- Episode ID: `0-1-6z51082994`
- HLS: `/drm1/inhousetranscoder/hls/TV_SHOWS/ZEE_TV/September2026/26092026/Episode/SPONSOR_SaReGaMaPa_2026_Ep3_Episode_26092026_hi_dcece26ca76cac6c5d5a51c6697144f7/index.m3u8`
- `isDrm: true`, `drmKey: d5011fc40b857febbfa76460839d5dc1`

---

## 3. CDN Access — Manifests and Segments

### HLS Master Manifest (accessible without auth)
```
GET https://mediacloudfront.zee5.com/drm/720p/movies/Hindi_Movies/Shridi_Ke_Sai_Baba_Hindi_Movie.mp4/index.m3u8
```
Returns a full HLS master playlist with quality options (144p → 720p), audio tracks, and subtitle tracks.

### HLS Variant Playlist (accessible without auth)
```
#EXTM3U
#EXT-X-VERSION:5
#EXT-X-KEY:METHOD=SAMPLE-AES,URI="skd://eb914881d23746c6b5d0f664235f2d48",KEYFORMAT="com.apple.streamingkeydelivery",KEYFORMATVERSIONS="1"
#EXTINF:6.000000,
segment-0.ts
...
```

### TS Segments (accessible without auth)
Segments are downloadable (e.g., `segment-0.ts` = 90,804 bytes, valid MPEG-TS). The container is intact but **PES payload is SAMPLE-AES encrypted** — every NAL unit is encrypted with the content key. Without the FairPlay/Widevine decryption key the video is undecodable.

### DASH/MPD Manifest (accessible without auth)
Contains:
- `cenc:default_KID` — the Widevine key ID
- PlayReady PSSH (Base64-encoded `WRMHEADER`)  
  - LA_URL: `http://pr-keyos.licenseKeyserver.com/core/rightsmanager.asmx`
- Widevine PSSH (standard `edef8ba9-…` UUID)
  - License server string in PSSH: `buydrmkeyos` (BuyDRM/KeyOS platform)

---

## 4. DRM Architecture

```
Content Encryption:
  HLS:  SAMPLE-AES (FairPlay-compatible key ID via skd:// URI)
  DASH: CENC (Common Encryption) — Widevine + PlayReady dual-DRM

License Servers:
  Widevine:   POST https://spapi.zee5.com/widevine/getLicense
  PlayReady:  http://pr-keyos.licenseKeyserver.com/core/rightsmanager.asmx
  Platform:   BuyDRM / KeyOS

DRM Key ID format (in API response `drmKey` field):
  UUID: eb914881-d237-46c6-b5d0-f664235f2d48
  HEX:  eb914881d23746c6b5d0f664235f2d48 (used in skd:// URI without hyphens)

License acquisition flow (app):
  1. App opens content → gets video.drmKey from GraphQL
  2. ExoPlayer requests Widevine license:
       POST https://spapi.zee5.com/widevine/getLicense
       Headers: x-access-token (user auth token), content-type, device-id, etc.
       Body: Widevine license challenge (binary)
  3. Server validates user subscription and returns license
  4. ExoPlayer decrypts and plays
```

---

## 5. Billing / Subscription Gate

The API returns `billingType: ""` (empty string) and `tier: ""` for all content when accessed with a platform token only (no user). The server withholds this information for anonymous requests.

**Observation:** All content queried has `isDrm: true`, including content in collections explicitly labelled "Free." The DRM layer is universal — there is no unencrypted AVOD stream tier. "Free" content is distinguished from SVOD at the **license server** level, not at the CDN/stream level. A valid (but subscription-less) user account would presumably receive a license for AVOD content.

---

## 6. Content ID Reference

| Prefix | Asset Type |
|--------|-----------|
| `0-0-XXX` | Movie |
| `0-1-XXX` | Episode |
| `0-2-XXX` | Season |
| `0-6-XXX` | TV Show |
| `0-8-XXX` | Collection / Rail |
| `0-101-XXX` | External Link content |

---

## 7. Key Findings Summary

| Finding | Detail |
|---------|--------|
| Platform token obtainable without login | `launchapi.zee5.com/launch?platform_name=android_app` |
| Movie video URLs exposed in GraphQL | `tvShowRelatedContent` query |
| Episode video URLs exposed in GraphQL | `GetEpisodes` query with `seasonId` |
| HLS manifests accessible without auth | `mediacloudfront.zee5.com` CDN |
| TS segment files downloadable without auth | CDN, ~90KB per 6-second segment |
| ALL content DRM-encrypted | SAMPLE-AES (HLS) + CENC Widevine/PlayReady (DASH) |
| DRM key IDs exposed in API | `video.drmKey` field in GraphQL |
| License server for Widevine | `spapi.zee5.com/widevine/getLicense` (requires user auth) |
| License server for PlayReady | `pr-keyos.licenseKeyserver.com` via BuyDRM/KeyOS |
| `billingType` not returned to anonymous users | Field returns `""` (empty) |
| Introspection disabled | Cannot enumerate full schema |

---

## 8. "God Mode" Verdict

**Can paid content be accessed for free?** No viable path found:

1. Video URL paths are obtainable without login ✓  
2. Manifests and TS/MP4 segment files download without auth ✓  
3. **Segments are SAMPLE-AES encrypted** — undecodable without a license ✗  
4. **Widevine license requires a user auth token** — no bypass found ✗  
5. `billingType` is hidden from anonymous requests ✗  

The DRM enforcement is at the license-server level. Even if a user has a valid account (no subscription), getting a Widevine license for SVOD content would fail server-side. No content was found without DRM protection.
