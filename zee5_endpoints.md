# Zee5 APK Endpoint Analysis
**App:** `com.graymatrix.did` (Zee5) v39.61.8  
**File:** `Zee 5_com.graymatrix.did_39.61.8.apks` (94MB)  
**Analyzed:** 2026-09-26  
**Total unique endpoints found:** 412

---

## Zee5 Production API Endpoints

### Authentication & User
| Endpoint | Purpose |
|----------|---------|
| `https://auth.zee5.com` | Authentication (login/register/refresh) |
| `https://user.zee5.com` | User profile management |
| `https://uapi.zee5.com` | User API (legacy/alternate) |
| `https://profiles.zee5.com` | User profiles |
| `https://useraction.zee5.com` | User actions (watch, like, bookmark) |
| `https://useraction.zee5.com/token/platform_tokens.php?platform_name=android_app` | Platform token fetch |
| `https://useraction.zee5.com/user` | User endpoint |
| `https://useraction-crm.zee5.com` | CRM user actions |
| `https://user-referral.zee5.com` | Referral system |
| `https://rewards.zee5.com/login` | Rewards login |

### Content & Catalog
| Endpoint | Purpose |
|----------|---------|
| `https://catalogapi.zee5.com` | Content catalog |
| `https://contentapi.zee5.com` | Content delivery |
| `https://contentbitrates.zee5.com` | Bitrate/quality config |
| `https://recoapi.zee5.com` | Recommendations |
| `https://featurelist.zee5.com` | Feature flags/config |
| `https://launchapi.zee5.com` | App launch config |
| `https://engagez.zee5.com` | Engagement/content |
| `https://nimbus.zee5.com` | Content/ads serving |
| `https://xtra.zee5.com` | Xtra content tier |
| `https://microdrama-playback-api.zee5.com` | Microdrama playback |
| `https://musicapi.zee5.com` | Music API |
| `https://cerberus.zee5.com` | Content gating/access control |

### Playback & Streaming
| Endpoint | Purpose |
|----------|---------|
| `https://spapi.zee5.com` | Streaming/playback API |
| `https://spapi.zee5.com/widevine/getLicense` | Widevine DRM license |
| `https://gapi.zee5.com/v1/consumer` | Consumer/gateway API |
| `https://gwapi.zee5.com` | Gateway API |
| `https://hipigwapi.zee5.com` | HiPi (short-video) gateway |
| `https://whapi.zee5.com` | Watch history API |
| `https://whapi-prod-node.zee5.com` | Watch history (Node) |
| `https://watchhistory.zee5.com` | Watch history |
| `https://service-polling-prod.zee5.com` | Service polling |

### Payments & Subscriptions
| Endpoint | Purpose |
|----------|---------|
| `https://securepayment.zee5.com` | Secure payments |
| `https://zpay-transformer.zee5.com` | Payment transformer |
| `https://subscriptionapi.zee5.com` | Subscriptions v1 |
| `https://subscriptionapiv2.zee5.com` | Subscriptions v2 |
| `https://oms-co.zee5.com` | Order management |
| `https://shopping.zee5.com/v3.9` | Shopping/commerce |
| `https://cpapi.zee5.com` | Content purchase API |

### Social, Games & Other
| Endpoint | Purpose |
|----------|---------|
| `https://api-games.zee5.com` | Games API |
| `https://gambit.zee5.com` | Gambit (games platform) |
| `https://games-leaderboard.zee5.com` | Games leaderboard |
| `https://usercomments.zee5.com` | User comments |
| `https://videolikedislike.zee5.com` | Video likes/dislikes |
| `https://track.zee5.com` | Tracking/analytics |
| `https://zauditions.zee5.com` | Zee Auditions |
| `https://b2bapi.zee5.com` | B2B API |
| `https://as.zee5.com/partners` | Partner/affiliate |
| `https://artemis.zee5.com/artemis/graphql` | GraphQL API |
| `https://quickmark.zee5.com/TENANT/qm/v2/surfaces` | QR/quick mark |
| `https://engagez.zee5.com` | Engagement API |
| `https://bulletshorts.com/show` (via `https://www.bulletshorts.com/show`) | BulletShorts content |

### CDN & Static Assets
| Endpoint | Purpose |
|----------|---------|
| `https://akamaividz2.zee5.com/image/upload` | Akamai image CDN |
| `https://imgstg.zee5.com/image/upload` | Image staging CDN |
| `https://zee5-ressh.cloudinary.com/image/upload` | Cloudinary image CDN |
| `https://mediacloudfront.zee5.com` | Media CloudFront CDN |
| `https://mediacloudfront.zee5.com/splash/Z5_MOBILE_V12_23MAR26.mp4` | Splash video |
| `https://stcf1.zee5.com` | Static content frontend |
| `https://stcf-prod.zee5.com/prod/android/sos/v1/config.json` | SOS config |

### Real-time / WebSocket
| Endpoint | Purpose |
|----------|---------|
| `https://ama-service-v2.zee5.com` | AMA (live streaming service) |
| `https://ama-ivs-auth.zee5.in` | AWS IVS auth for live |
| `https://zee-dev-realtime-c3e3hpacd5hfduh9.z01.azurefd.net/.well-known/mercure` | Mercure (SSE/realtime, Azure) |

---

## Zee5 Non-Production Endpoints (Dev / QA / UAT)

| Endpoint | Environment |
|----------|------------|
| `https://auth-qa.zee5.dev` | QA |
| `https://auth-uat-gcp.zee5.com` | UAT |
| `https://catalogapi-uat-gcp.zee5.com` | UAT |
| `https://country-qa.zee5.dev` | QA |
| `https://country-uat-gcp.zee5.com` | UAT |
| `https://gwapi-qa.zee5.dev` | QA |
| `https://gwapi-uat-gcp.zee5.com` | UAT |
| `https://launch-qa.zee5.dev` | QA |
| `https://launch-uat-gcp.zee5.com` | UAT |
| `https://oms-co-qa.zee5.dev` | QA |
| `https://oms-co-uat-gcp.zee5.com` | UAT |
| `https://securepayment-qa.zee5.dev` | QA |
| `https://securepayment-uat-gcp.zee5.com` | UAT |
| `https://subscriptionapi-qa.zee5.dev` | QA |
| `https://subscriptionapi-uat-gcp.zee5.com` | UAT |
| `https://user-qa.zee5.dev` | QA |
| `https://user-uat-gcp.zee5.com` | UAT |
| `https://useraction-qa.zee5.dev` | QA |
| `https://useraction-uat-gcp.zee5.com` | UAT |
| `https://pwa.uat.zee5.dev` | UAT (PWA) |
| `https://stcf-nonprod.zee5.com` | Non-prod static |
| `https://gambit-dev.zee5.be` | Dev (Belgium) |
| `https://sputnik-dev.zee5.be` | Dev (Belgium) |
| `https://zee5-whapi-pt.zee5.io` | Portugal staging |
| `https://zee5-whapi-qc-1.zee5.be` | QC (Belgium) |
| `https://zee-dev-cnbtdmhwckckc8ep.z01.azurefd.net/client` | Azure dev |
| `https://zee-dev-realtime-c3e3hpacd5hfduh9.z01.azurefd.net` | Azure dev realtime |
| `https://pwa-7438-2zodnnhc4q-el.a.run.app` | GCP Cloud Run (staging PWA) |
| `https://mtkikwb8yc.execute-api.ap-south-1.amazonaws.com/prod/appevent` | AWS Lambda (ap-south-1) |

---

## Third-Party Integrations

### Payments
| Provider | Endpoints |
|----------|-----------|
| **Juspay** | `https://api-ns1.juspay.in`, `https://api-ns3.juspay.in`, `https://payments.juspay.in`, `https://sandbox.juspay.in`, `https://logs.juspay.in/godel/analytics`, `https://logs.juspay.io/godel/analytics`, `https://debug.logs.juspay.net/godel/analytics`, `https://public.releases.juspay.in`, `https://assets.juspay.in` |
| **Adyen** | `https://checkoutshopper-live.adyen.com/checkoutshopper`, `https://checkoutshopper-live-in.adyen.com/checkoutshopper` + APSE/AU/NEA/US regions, `https://checkoutanalytics-live.adyen.com/checkoutanalytics` (all regions + test) |
| **Amazon Pay** | `https://amazonpay.amazon.in/v3/sdk/crash-events`, `https://amazonpay.amazon.in/v3/sdk/metric-events`, `https://api.amazon.in`, `https://lwa.amazon.in`, `https://apac.account.amazon.com`, `https://na.account.amazon.com`, `https://eu.account.amazon.com` |
| **PayU** | `https://static.payu.com/sites/terms/files/payu_privacy_policy_cs.pdf` (privacy docs) |
| **Square/CashApp** | `https://api.cash.app/customer-request/v1`, `https://sandbox.api.cash.app/customer-request/v1`, `https://api.squareup.com` |
| **Olamoney** | `https://olamoney.com` |
| **Reload.in** | `https://www.reload.in/recharge` |
| **MSISDN/AOC** | `https://msisdn.mife-aoc.com/api/aoc?aocToken` |

### Analytics & Attribution
| Provider | Endpoints |
|----------|-----------|
| **Firebase Analytics** | `https://app-measurement.com/a`, `https://app-measurement.com/s/d` |
| **Mixpanel** | `https://api.mixpanel.com/track`, `https://api.mixpanel.com/engage`, `https://api.mixpanel.com/groups` |
| **AppsFlyer** | `https://privacy-sandbox.appsflyersdk.com/api/trigger` (+ dynamic `%s` template URLs for conversions/impressions/launches/registers) |
| **NPAW/Youbora** | `https://gnsnpaw.com`, `https://experiments.npaw.com/assign`, `https://stage-smartswitchv2.youbora.com` |
| **Google Analytics** | `https://www.google-analytics.com`, `https://ssl.google-analytics.com` |
| **Comscore** | `https://sb.scorecardresearch.com/p2`, `https://segment-data-us-east.zqtk.net` |

### Advertising
| Provider | Endpoints |
|----------|-----------|
| **Google Ads / DoubleClick** | `https://googleads.g.doubleclick.net`, `https://pubads.g.doubleclick.net`, `https://pagead2.googlesyndication.com`, `https://www.googleadservices.com` |
| **Google IMA SDK** | `https://imasdk.googleapis.com/admob/sdkloader/native_video.html`, `https://imasdk.googleapis.com/native/sdkloader/native_sdk_v3.html`, `https://imasdk.googleapis.com/pal/key/public.json` |
| **AdMob** | `https://admob-gmats.uc.r.appspot.com` |

### Authentication (3rd Party)
| Provider | Endpoints |
|----------|-----------|
| **Firebase Auth** | `https://firebaseinstallations.googleapis.com/v1`, `https://firebaseremoteconfig.googleapis.com/v1/projects`, `https://firebaseremoteconfigrealtime.googleapis.com/v1/projects` |
| **Google Sign-In** | `https://accounts.google.com/o/oauth2/revoke?token`, `https://www.googleapis.com/auth/userinfo.email` |
| **Facebook Login** | `https://*.facebook.com`, `https://facebook.com/device?user_code=%1` |
| **Truecaller** | `https://sdk-otp-verification-noneu.truecaller.com/v1/otp/client/installation`, `https://sdk-otp-verification-noneu.truecaller.com/v3/otp/installation`, `https://outline.truecaller.com/v1` |
| **OTPless** | `https://otpless.com/mobile/index.html` |

### Privacy & Compliance
| Provider | Endpoints |
|----------|-----------|
| **OneTrust** | `https://mobile-data.onetrust.io/cfw/cmp/v1/banner`, `https://mobile-data.onetrust.io/cfw/cmp/v1/preferences`, `https://mobile-data.onetrust.io/cfw/cmp/v1/save-log-consent`, `https://mobile-data.onetrust.io/cfw/cmp/v1/uc-purposes`, `https://mobile-data.onetrust.io/cfw/cmp/v1/vendors` |
| **1Trust** | `https://geolocation.1trust.app` |
| **Google Funding Choices** | `https://fundingchoicesmessages.google.com/a/consent` |

### Crash & Remote Config
| Provider | Endpoints |
|----------|-----------|
| **Firebase Crashlytics** | `https://firebase-settings.crashlytics.com/spi/v2/platforms/android/gmp` |
| **Google Play Integrity** | Via Play Services |

### Maps
| Provider | Endpoints |
|----------|-----------|
| **Google Maps** | `https://maps.google.com/maps?q`, `https://maps.googleapis.com/maps/api/place/nearbysearch/json` |
| **Zoho Maps** | `https://maps.zoho.com/api/v2/search`, `https://maps.zoho.com/v2/staticimage` |

### Miscellaneous SDKs
| Provider | Endpoints |
|----------|-----------|
| **reCAPTCHA** | `https://www.recaptcha.net/recaptcha/api3` |
| **Mobilisten (Freshchat)** | `https://mobilisten.io` |
| **WeChat** | `https://open.weixin.qq.com/connect/sdk/qrconnect`, `https://long.open.weixin.qq.com/connect/l/qrconnect` |
| **AppsFlyer OneLink** | `https://zee5.onelink.me/RlQq/WATCHZEE5NOW` |
| **Bingapis** | `https://www.bingapis.com` |

---

## Key API Paths

```
# Auth
POST https://auth.zee5.com/...
GET  https://useraction.zee5.com/token/platform_tokens.php?platform_name=android_app

# Playback / DRM
POST https://spapi.zee5.com/widevine/getLicense

# GraphQL
POST https://artemis.zee5.com/artemis/graphql

# Quick surfaces
GET  https://quickmark.zee5.com/TENANT/qm/v2/surfaces

# Consumer gateway
GET  https://gapi.zee5.com/v1/consumer

# SOS config
GET  https://stcf-prod.zee5.com/prod/android/sos/v1/config.json

# Juspay (payments) release config
GET  https://assets.juspay.in/hyper/bundles/in.juspay.merchants/zee5/android/release/manifest.json
GET  https://assets.juspay.in/hyper/configs/in.juspay.merchants/zee5/android/release/unified_config.json

# Splash video
https://mediacloudfront.zee5.com/splash/Z5_MOBILE_V12_23MAR26.mp4
```

---

## APK Structure Summary

```
zee5.apks
├── base.apk              (91.9 MB — main application)
├── split_config.arm64_v8a.apk  (4.8 MB — ARM64 native libs)
├── split_config.en.apk         (0.1 MB — English strings)
├── split_config.xxhdpi.apk     (1.6 MB — xxhdpi density resources)
├── icon.png
├── meta.sai_v1.json
└── meta.sai_v2.json

base.apk internals:
├── classes.dex … classes9.dex  (9 DEX files)
├── AndroidManifest.xml
├── assets/
├── res/
└── resources.arsc
```
