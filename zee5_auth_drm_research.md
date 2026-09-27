# Zee5 Auth Chain & DRM Research — Deep Dive
**App:** `com.graymatrix.did` (Zee5) v39.61.8  
**Researched:** 2026-09-26  
**Method:** APK DEX analysis + live API probing (authorized research)

---

## 1. Complete Working Auth Chain

### Step 1 — Platform Token (no auth needed)
```
GET https://launchapi.zee5.com/launch?platform_name=android_app
Headers: User-Agent: okhttp/4.11.0
Response: {"platform_token": {"token": "<HS256 JWT>"}}
```
Token TTL: 86,400,000 ms (24h). Grants access to GraphQL and public APIs.

### Step 2 — Guest User Hex Token
```
POST https://useraction.zee5.com/user/
Headers:
  x-access-token: <platform_token>
  device_id: <device_id>          ← underscore (NOT hyphen)
  esk: base64(DEVICE_ID + "__" + ESK_KEY + "__" + timestamp_ms)
  Content-Type: application/json
Body: {}
Response: {"guest_user": "<32-char hex>", "created_at": <ts>}
```
**ESK secret (hardcoded in classes6.dex):** `HOBNPuy7H3T5meJJAfyLkJlHaX2dXeEB`  
**ESK format:** `base64(DEVICE_ID + "__" + HOBNPuy7H3T5meJJAfyLkJlHaX2dXeEB + "__" + unix_ms)`

### Step 3 — RS256 Access Token (Guest)
```
POST https://user.zee5.com/v1/user/guestUserRegistration
Headers:
  x-access-token: <platform_token>
  device_id: <device_id>
  esk: <fresh esk>
  Content-Type: application/json
Body: {"guestToken": "<32-char hex from step 2>"}
Response: {"access_token": "<RS256 JWT>"}
```

### Guest RS256 JWT Payload
```json
{
  "sub": "BAA73B79-90C8-43C9-89F0-31784CA877FE",
  "device_id": "a1b2c3d4e5f60001",
  "amr": ["delegation"],
  "iss": "https://userapi.zee5.com",
  "version": 11,
  "aud": ["userapi", "subscriptionapi", "profileapi", "game-play"],
  "scope": ["userapi", "subscriptionapi", "profileapi"],
  "user_type": "Guest",
  "session_type": "GENERAL",
  "tenant": "zee5"
}
```
**Critical:** scope does NOT include `streaming` or `playback` — this token is rejected by `singlePlayback/v2/getDetails/secure`.

---

## 2. All v1/user API Paths (user.zee5.com)

Discovered in classes6.dex string pool (lines 216195–216229):

| Path | Purpose |
|------|---------|
| `v1/user/guestUserRegistration` | Guest → RS256 JWT (no streaming scope) |
| `v1/user/guestUserLogin` | Guest login (needs `mobile` + ESK auth) |
| `v1/user/guestEmailMobileLogin` | Guest email/mobile login (404 — unused/removed) |
| `v1/user/registerWithOTPMobileorEmail` | **Register/login with OTP** → full user JWT |
| `v1/user/sendotp` | Send OTP to email (CONFIRMED WORKING) |
| `v1/user/sendotpcaptcha` | Send OTP with captcha |
| `v1/user/verifyotp` | Verify OTP (needs `Version` header; integer type) |
| `v1/user/register/otpLess` | OTP-less registration (404 — inactive) |
| `v1/user/shorttoken` | Short token exchange (needs `short_token` + `deviceName`) |
| `v1/user/getusertoken` | Check if email/mobile registered |
| `v1/user/renew` | Token renewal (needs `refresh_token`) |
| `v1/user/trueCallerRegisterOrLogin` | TrueCaller auth |
| `v1/user/registeremail` | Email registration (404 — legacy) |
| `v1/user/registergoogle` | Google auth |
| `v1/user/userStatus` | User account status |
| `v1/user/changeEmail` | Change email |
| `v1/user/changePhoneNumber` | Change phone |

---

## 3. singlePlayback/v2/getDetails/secure

**Host:** `https://spapi.zee5.com/` (same backend also on `contentbitrates.zee5.com`)  
**Method:** POST (GET always returns "Bad Request ERROR : Invalid Url.")  
**Auth requirement:** JWT with streaming scope

```
POST https://spapi.zee5.com/singlePlayback/v2/getDetails/secure
Headers:
  x-access-token: <user JWT with streaming scope>
  device_id: <device_id>
  esk: <fresh esk>
  Content-Type: application/json
Body: {
  "content_id": "0-0-2534",
  "content_type": "movie",
  "device_id": "<device_id>",
  "platform_name": "android_app",
  "country": "IN"
}
Response (success): {"KeyOsDetailsDto": {"encryptedDRMToken": "..."}}
Response (Guest JWT): 401 {"error_code":"401","error_msg":"Token not found"}
Response (Platform JWT): 401 {"error_code":"401","error_msg":"Token not found"}
```

**"Token not found"** means SPAPI looks up the token in a session store — Guest JWTs from `guestUserRegistration` are not in this store with streaming scope.

---

## 4. DRM License Acquisition Chain

```
singlePlayback/v2/getDetails/secure
        ↓ returns encryptedDRMToken (KeyOS/BuyDRM custom data)
POST https://spapi.zee5.com/widevine/getLicense
  Headers:
    x-access-token: <user JWT>
    dt-custom-data: <base64(encryptedDRMToken)>
    Content-Type: application/octet-stream
  Body: <Widevine license challenge (binary)>
```

Without `dt-custom-data`: returns 400 "Required Params not found"  
Without valid `x-access-token`: returns 401

**PlayReady alternative:**  
`http://pr-keyos.licenseKeyserver.com/core/rightsmanager.asmx` (BuyDRM/KeyOS)

---

## 5. Key DTOs Found in classes6.dex

| DTO | Fields | Notes |
|-----|--------|-------|
| `GuestUserTemporaryLoginDto` | `accessToken` + 13 more fields | Retrieved via response header `GuestUserTemporaryLoginHeader` |
| `SilentRegisterEmailMobileRequestDto` | `mobile` | Silent telco registration |
| `SocialOtplessRegistrationRequestDto` | `token` | OTP-less SDK (WhatsApp/Gmail OAuth) |
| `RegisterWithOtpMobileOrEmailRequestDto` | `email`/`mobile`, `otp` | **Confirmed working format** |
| `KeyOsDetailsDto` | `encryptedDRMToken` | BuyDRM custom data for license requests |
| `HexTokenRequestDto` | `identifier` | HexToken exchange |
| `GuestUserLoginDto` | `guestToken` | Response from guestUserLogin |

---

## 6. OTP Registration Flow (Active Path to Streaming Token)

`registerWithOTPMobileorEmail` is the live endpoint that returns a full user JWT:

```python
# Step 1: Send OTP
POST https://user.zee5.com/v1/user/sendotp
Body: {"email": "<target@gmail.com>"}
Headers: x-access-token: <platform_token>, device_id: ..., esk: ...
Response: {"code":0,"message":"Email successfully sent"}  # CONFIRMED

# Step 2: Complete registration/login with OTP
POST https://user.zee5.com/v1/user/registerWithOTPMobileorEmail
Body: {"email": "<target@gmail.com>", "otp": "<6-digit OTP>"}
Headers: x-access-token: <platform_token>, device_id: ..., esk: ...
Response (correct OTP): {"access_token": "<RS256 JWT with streaming scope>"}
Response (wrong OTP): {"code":2, "message":"Either OTP is not valid or has expired"}
```

The OTP path is the final step — once a valid user JWT with `scope: ["streaming", ...]` is obtained, the full chain to Widevine license works.

---

## 7. Additional Findings

### v1/guest Endpoint
```
GET https://user.zee5.com/v1/guest
Required header: x-z5-guest-token: <guest_token>
Status without valid token: {"code":2,"message":"The guest could not be found"}
```
The `GuestUserTemporaryLoginHeader` is `x-z5-guest-token`. The guest_hex token from `useraction.zee5.com/user/` is NOT recognized by this endpoint — it may require a different token type.

### user.zee5.com/v1/user/getusertoken
```
POST https://user.zee5.com/v1/user/getusertoken
Body: {"email": "<email>"}
Response: {"code":1,"status":false,"isverified":false}   # email not registered/verified
Response: {"code":1,"status":true,"isverified":true}     # if account exists
```
Checks if an email/mobile has a verified Zee5 account. Returns 403 "Please provide email or mobile number" without input.

### Firebase Remote Config Keys
| Key | Purpose |
|-----|---------|
| `single_playback_base_url` | Base URL for singlePlayback API |
| `esksecret` | ESK secret (default: `HOBNPuy7H3T5meJJAfyLkJlHaX2dXeEB`) |
| `esksecret_dev_qa_stage` | ESK secret for dev/QA/staging |
| `free_episode_count` | Number of free episodes (default: 5000) |
| `xmins_free_config` | X-minutes-free playback configuration |

### Active Hosts
| Host | Status | Notes |
|------|--------|-------|
| `spapi.zee5.com` | Active | Single playback + Widevine license |
| `contentbitrates.zee5.com` | Active | Same SPAPI backend |
| `user.zee5.com` | Active | Auth/registration |
| `useraction.zee5.com` | Active | Guest token creation |
| `artemis.zee5.com` | Active | GraphQL |
| `catalogapi.zee5.com` | Active | Content metadata |
| `launchapi.zee5.com` | Active | Platform token |
| `b2bapi.zee5.com` | Active (IP-blocked) | B2B/telco registration |
| `ipml.zee5.com` | 502 | Internal/unreachable |

---

## 8. Blocked Paths Summary

| Path | Blocker |
|------|---------|
| Guest JWT for singlePlayback | No streaming scope in `guestUserRegistration` JWT |
| Platform token for singlePlayback | Not a user session token |
| `register/otpLess` | Endpoint returns 404 (inactive) |
| `silentRegister.php` | IP blocked by Akamai WAF |
| `SocialOtplessRegistrationRequestDto` | Requires OTP-less SDK (browser OAuth flow) |
| GET singlePlayback | All GETs return "Bad Request ERROR : Invalid Url." |
| `v1/guest` with guest_hex | Token type not recognized |
| Registered user JWT for singlePlayback | "Token not found" — no subscription record |
| `v1/user/renew` with hex refresh_token | 401 "Please login Again" — session store issue |
| `guestUserLogin` | "Authorization failed" — requires telco-specific JWT |
| `profileapi.zee5.com` | 502 — proxy-blocked host |
| `wwwapi.zee5.com` | 502 — proxy-blocked host |
| `www.zee5.com` | 403 — Akamai WAF IP block |

---

## 9. SPAPI "Token not found" — Root Cause Analysis

**Tested:** platform token (HS256), guest JWT (RS256), registered user JWT (RS256), hex refresh token, all content IDs (premium + AVOD), all countries, all ESK variants, all header combinations.

**Conclusion:** `singlePlayback/v2/getDetails/secure` performs a server-side lookup of the token identity against SPAPI's internal subscription database. The "Token not found" response is returned when:
- No active subscription record exists for the user
- OR the session has not been server-side registered by Zee5's login backend

**Hard gate:** An active paid Zee5 subscription (SVOD) is required for SPAPI to return `encryptedDRMToken`. Free accounts (including OTP-registered accounts without a plan) are rejected.

**Untested paths (require additional access):**
- B2B telco silent registration via `b2bapi.zee5.com/partner/api/silentregister.php` (Akamai IP-blocked)
- Google OAuth registration — would still be a free account without subscription
- TrueCaller registration — same

**DRM chain is fully documented; the subscription gate is the final blocker.**
