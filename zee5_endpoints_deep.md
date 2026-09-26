# Zee5 APK — Deep Endpoint & API Analysis
**App:** `com.graymatrix.did` (Zee5) v39.61.8  
**Analyzed:** 2026-09-26

---

## GraphQL API — All Operations
**Endpoint:** `POST https://artemis.zee5.com/artemis/graphql`

### Queries (read)
| Operation | Purpose |
|-----------|---------|
| `GetCollections` | Home/landing page rail collections |
| `GetEpisodes` | Episode listing for a TV show |
| `GetShowEpisodes` | Episodes by show ID |
| `GetSearchResult` | Search content (movies, shows, episodes) |
| `GetSearchResultsRail` | Search results in rail format |
| `GetHybridSearchResultsRail` | Hybrid search with userType filter |
| `GetSearchSuggestionQuery` | Autocomplete / type-ahead suggestions |
| `TrendingSearch` | Trending search terms |
| `SearchHomePage` | Search homepage layout |
| `SimilarContent` | Related/similar content recommendations |
| `RecommendedRecoQuery` | Recommendations |
| `GetCohortRecommendations` | Cohort-based personalised reco |
| `GetHyperRecommendations` | Hyper-personalised reco |
| `PersonalizedContent` | Personalised content rail |
| `UpNextEpisodes` | Up-next episode suggestions |
| `UpNextRecoQuery` | Up-next recommendation rail |
| `TvShowRelatedContentQuery` | Related content for a TV show |
| `TvShowSeasonsRelatedContentQuery` | Related content across seasons |
| `ContentProvider` | Content partner details |
| `GetTvodTierQuery` | TVOD pricing tier for content |
| `DisplayPlansQuery` | Subscription plans display |
| `ProductDetails` | Product/plan details |
| `DisplayAdsQuery` | Ad configuration by content |
| `AdsDeferredDeeplinkQuery` | Deferred deep link from ad |
| `GetPollsForAssetQuery` | Polls attached to an asset |
| `GetSequentialPollQuery` | Sequential poll flow |
| `GetIsLiveEventQuery` | Whether content is a live event |
| `GetLiveScoreQuery` | Live sports score |
| `GetLiveScoreDetailsQuery` | Detailed live score |
| `GetShortScoreCardQuery` | Short scorecard |
| `GetKeyMomentsQuery` | Key moments / highlights in a video |
| `GetMetaInfoQuery` | SEO meta info for content |
| `GetProgramsForChannels` | EPG programmes for live TV channels |
| `ChannelsByGenreQuery` | Channels grouped by genre |
| `GetLiveTvGenres` | Live TV genre list |
| `GoogleLoginQuery` | Google OAuth login |
| `FacebookLoginQuery` | Facebook login |
| `IsUserExistsQuery` | Check if user account exists |
| `SendOTPtoMobileQuery` | Send OTP to phone |
| `SendOTPtoEmailQuery` | Send OTP to email |
| `VerifyOTPFromMobileQuery` | Verify mobile OTP |
| `VerifyOTPFromEmailQuery` | Verify email OTP |
| `VerifyOTPTruecallerQuery` | Verify via Truecaller |
| `GetUserDetails` | User profile details |
| `GetProfilesWithCollection` | User profiles + content |
| `HasUserOnboardedToThirdPartyQuery` | Third-party onboarding status |
| `ThirdPartyAccessQuery` | Third-party access check |
| `SSOTagValidationQuery` | SSO tag / partner login validation |
| `IsUserRegisteredToGamification` | Gamification registration status |
| `GetWatchPartyRoom` | Watch party room details |
| `GetWatchPartyNickName` | Watch party nickname |
| `WatchNWinConfigQuery` | Watch & Win feature config |
| `WatchNWinContestsQuery` | Watch & Win contest list |
| `WatchAndWinLeaderBoardQuery` | Watch & Win leaderboard |
| `CampaignLeaderboard` | Campaign leaderboard |
| `TournamentLeaderboard` | Sports tournament leaderboard |
| `PlayerStandingInCampaign` | User rank in a campaign |
| `PlayerStandingInTournament` | User rank in tournament |
| `TeamDetailQuery` | Sports team details |
| `ContestantDetail` | Show contestant details |
| `PartnerSettingsQuery` | B2B partner settings by `partnerKey` |
| `UserRewards` | User reward/points balance |
| `LiveCommentaryHistoryQuery` | Live sports commentary history |
| `PostSequentialPollAnswerQuery` | Submit sequential poll answer |

### Mutations (write)
| Operation | Purpose |
|-----------|---------|
| `GoogleRegistrationMutation` | Register via Google |
| `FacebookRegistrationMutation` | Register via Facebook |
| `TrueCallerAndroidRegisterUserMutation` | Register via Truecaller |
| `VerifyOTPNewUserMutation` | Verify OTP for new user registration |
| `RemoveDeviceAfterLogout` | Remove device on logout |
| `AddToWatchListBasedOnProfile` | Add to watchlist (profile-scoped) |
| `DeleteFromWatchListBasedOnProfile` | Remove from watchlist |
| `DeleteAllFromWatchListBasedOnProfile` | Clear watchlist |
| `DeleteWatchHistory` | Delete watch history |
| `RegisterUserToGamification` | Enroll in gamification |
| `SubmitPollResponseMutation` | Submit poll answer |
| `CreateWatchPartyRoom` | Create a watch party room |
| `GenerateWatchPartyUserToken` | Get watch party user token |

---

## REST API Paths

### User & Auth (`auth.zee5.com`, `user.zee5.com`, `useraction.zee5.com`)
```
GET  /token/platform_tokens.php?platform_name=android_app   ← initial auth token
POST /user/v2/watchlist
GET  /user/profile
POST /v1/user/confirmmobile
POST /v1/user/initiateOtpProfilePin
POST /v1/user/setPin
POST /v1/user/verifyOtpForProfilePin
POST /auth/o2/token                                          ← OAuth token
POST /auth/relyingPartyLogout
POST /authTokens:generate
GET  /userRegistration
GET  /userStatus
POST /userConsentDialog
```

### Profiles (`profiles.zee5.com`)
```
GET/POST /v2/profiles
GET/PUT  /v2/profiles/{profileId}
GET/POST /v3/profiles
GET/PUT  /v3/profiles/{id}
GET      /v3/profilesAvatars
GET      /profileV3
```

### Watch History (`watchhistory.zee5.com`)
```
GET/POST /v1/watchhistory
GET/POST /v2/watchhistory
GET      /api/v1/watchhistory/playlist
POST     /api/v1/watchhistory/progress
GET      /api/v2/watchhistory
GET      /v1/watchlist
```

### Subscription (`subscriptionapi.zee5.com`, `securepayment.zee5.com`)
```
GET  /v1/subscriptionplan?
GET  /v1/subscriptionplan/{planid}?
POST /subscription/{gateway}/payments
POST /paymentGateway/{gateway}/prepare
POST /paymentGateway/{gateway}/callback
POST /paymentGateway/{gateway}/resentotp
GET  /paymentGateway/cancelSubscription/{transactionID}
GET  /paymentGateway/subscriptionRecurringStatus/{transactionID}
GET  /v1/workflow
GET  /subscribe_mobile
POST /subscribe_otp_validation
POST /subscribe_send_otp
GET  /subscriptionMini
GET  /subscriptionplan
GET  /sub
```

### Playback (`spapi.zee5.com`, `contentbitrates.zee5.com`)
```
POST /widevine/getLicense
POST /v1/{contentType}/prepare
POST /v1/{contentType}/prepare/purchase
GET  /api/v1/playback/shortdrama
```

### Comments (`usercomments.zee5.com`)
```
POST /v1.0/comment/createComment
DELETE /v1.0/comment/deleteComment
GET  /v1.0/comment/getAllComment
GET  /v1.0/comment/getAllReply
GET  /v1.0/comment/getUser
PUT  /v1.0/comment/updateComment
POST /v2.0/comment/createComment
DELETE /v2.0/comment/deleteComment
GET  /v2.0/comment/getAllComment
GET  /v2.0/comment/getAllReply
PUT  /v2.0/comment/updateComment
POST /v1.0/video/createUserAction
```

### Games (`api-games.zee5.com`, `gambit.zee5.com`)
```
GET  /games/data
POST /games/dataCollection
POST /games/feedback
GET  /games/puzzle
GET  /games/recentlyPlayed
GET  /games/userdata
POST /games/udcSubmitFeedback
```

### Partner / B2B / Telco (`b2bapi.zee5.com`)
```
POST /partner/api/silentregister.php     ← telco silent registration
GET  /partner/eduauraa/sso.php           ← EduAuraa SSO
POST /v1/mife/callback                   ← MIFE/AOC telco callback
GET  /crs/api/getMetadata
GET  /crs/api/episode/getShowEpisodes
GET  &subs_type=telco&platform=android   ← telco subscription param
```

### Content / Catalog (`contentapi.zee5.com`, `catalogapi.zee5.com`)
```
GET  /content/collection/{id}
GET  /content/trailer/{id}
GET  /content/tvshow/{id}
```

### Consumer Gateway (`gapi.zee5.com`)
```
GET  /v1/consumer/
```

### Microdrama (`microdrama-playback-api.zee5.com`)
```
GET  /api/v1/playback/shortdrama
```

### Quick Surfaces (`quickmark.zee5.com`)
```
GET  /TENANT/qm/v2/surfaces
```

### Shopping (`shopping.zee5.com`)
```
GET  /v3.9/
```

### SOS Config (`stcf-prod.zee5.com`)
```
GET  /prod/android/sos/v1/config.json    ← app SOS / emergency config
```

---

## Feature Flags & Remote Config

### Unleash Feature Flags
The app uses **Unleash** for feature toggles, fetched at runtime. Key flags found:
```
feature_is_avod_download_disabled
feature_xr_server_polling_and_voting_enabled
feature_zee5_games_page_visible_to_avod
feature_zee5_games_rail_visible_to_avod
is_eduaraa_free_trial_flow_enabled
x_min_playback_free_config_save_interval_ms
android_subscription_remote_configurations
```

### AWS AppConfig (Remote Config)
```
ARN: arn:aws:remote-config:us-west-2:377838819204:appConfig:a0dfwasf
Region: us-west-2
Account ID: 377838819204
```

### AWS Lambda (Event tracking)
```
POST https://mtkikwb8yc.execute-api.ap-south-1.amazonaws.com/prod/appevent
Region: ap-south-1
```

### Launch Config Keys (`launchapi.zee5.com`)
```
xrserver_base_url
xrserver_sse_base_url
xrserver_sse_service
xrserver_login_data
x_access_token_refresh_url
xtraAPI
free_episode_count          (default: 5000)
x_min_free_episode_count
x_min_live_free_duration
xmins_free_config
subscription_language_plan_page
subscription_page_variant_version
```

---

## Telco / Carrier Subscription Flow

Full telco billing integration found — Axinom + MIFE:

```
Providers: Axinom, MIFE (Mobile Initiated Flow Extended / AOC)
Auth:    POST https://msisdn.mife-aoc.com/api/aoc?aocToken=...
Flow:
  1. App calls /partner/api/silentregister.php  → gets telco session
  2. App calls /v1/mife/callback                → MIFE OTP callback
  3. Axinom validates:  AxinomResponseDto
     DTOs: TelcoPrepareRequestDto, TelcoPrepareResponseDto,
           TelcoOtpRequestDto, TelcoOtpResponseDto,
           MifePrepareRequestDto, MifePrepareResponseDto,
           MifeValidateOtpRequestDto, MifeValidateOtpResponseDto
```

---

## XR Server (Live Interactive / Gamification)
Separate authenticated real-time server for polling/voting during live events:

```
Config keys (from launchapi):
  xrserver_base_url
  xrserver_sse_base_url    ← Server-Sent Events
  xrserver_sse_service
  xrserver_login_data

Auth: XRServerAuthenticationUseCase → sessionTicket → getValidatedXRServerToken
Headers: applyXRServerHeaders

DTOs: XRServerDto, PlayerProfileDto, LeaderboardDto, InventoryDataDto,
      PollResultDto, PredictivePollDto, AnswerPollRequestDto,
      AnswerPredictionRequestDto, TournamentLeaderboardRequestDto,
      MatchLeaderboardRequestDto, GlobalVariableDto, PlayfabDataDto
```
(Uses **PlayFab** backend — Microsoft gaming platform)

---

## Deep Links

```
zee5://
zee5://www.zee5.com
https://www.zee5.com/channels/details/{id}
https://www.zee5.com/livetv
https://www.zee5.com/tvshows
https://www.zee5.com/zee5originals
https://www.zee5.com/USReferral
https://www.zee5.com/paymentsuccess
https://www.zee5.com/paymentfailure
https://www.zee5.com/paymentcancelled
https://www.zee5.com/know-your-team
https://www.zee5.com/help
https://www.zee5.com/xrserverplaceholder
https://zee5.onelink.me/RlQq/WATCHZEE5NOW
```

---

## CDN Image Transform API (`akamaividz2.zee5.com`)

Supports Cloudinary-style transforms in the URL path:
```
/image/upload/c_scale,f_webp,q_auto:eco,w_{width}/{asset_path}
/image/upload/c_fill/{asset_path}
/image/upload/w_1080/{asset_path}
/image/upload/master/{asset_path}

Examples:
/image/upload/c_scale,f_webp,q_auto:eco,w_1080/frontend/consumption/gating/gating_background.png
/image/upload/frontend/language_icons_v2/Z5_{language_code}_Default.png
/image/upload/frontend/language_icons_v2/Z5_{language_code}_Selected.png
/image/upload/commerce/signupnudgebanner.jpg
```

---

## Watch Party

```
Mutations: CreateWatchPartyRoom, GenerateWatchPartyUserToken
Queries:   GetWatchPartyRoom, GetWatchPartyNickName
SSE:       Real-time sync via xrserver_sse_base_url
```

---

## Help / Support
```
https://helpcenter.zee5.com/portal/en/home
https://helpcenter.zee5.com/portal/en/kb/articles/content-grievance-redressal
```
