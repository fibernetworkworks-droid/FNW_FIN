# BSNL Copper-to-FTTH API Flow — DSCM Portal

**Base URL:** `https://wsc.cdr.bsnl.co.in/portal/drm/api`  
**Auth:** SESSION cookie (`SESSION=<token>` from DRM portal login)  
**Session IDs:** userId=307710, orgId=307710, areaId=178388  
**All requests:** POST with `Content-Type: application/json`

---

## Flow 1: Individual Subscriber Shifting (Copper LL → FTTH)

### Step 1 — Find Customer
```
POST /ding/custService/qryCustListBsnl
{
  "custName": "...",       // optional
  "mobile": "9XXXXXXXXX",  // optional
  "pageIndex": 1,
  "pageSize": 10
}
Response: {
  "custDtoList": [{
    "custId": "1100600000",
    "custCode": "11100600000",
    "custName": "CUSTOMER NAME",
    "custType": "A"
  }]
}
```

### Step 2 — Get Subscriber List
```
POST /ding/subsService/qrySubsListBsnl
{"custId": "1100600000", "pageIndex": 1, "pageSize": 10}

Response: {
  "subsDtoList": [{
    "subsId": "...",
    "subsNbr": "0832XXXXXXX",
    "serviceType": "LL",
    "acctNbr": "...",
    "available_flag": "Y"
  }]
}
```

### Step 3 — Address Lookup (FTTH Install Location)
```
POST /ding/custService/qryOssAddressListBsnl
{
  "addressReq": {
    "addressId": "178388",   // areaId or parent address ID
    "addressLevel": "DOWN"   // go one level down
  }
}
Response: {
  "addrs": [{
    "addressId": "...",
    "addressName": "...",
    "addressLevel": "..."
  }],
  "totalCount": "N",
  "returnCode": "0"
}
```

### Step 4 — Check Shifting Eligibility
```
POST /ding/subsService/subsShiftingCheckBsnl
{
  "subsId": "<subsId from Step 2>",
  "installationAddressId": "<addressId from Step 3>"
}
Response: {
  "returnCode": "0",           // "0" = eligible
  "returnMsg": "Success",
  "shiftingFlag": "Y",         // Y = can shift
  "offerFlag": "Y",            // Y = plans available
  "accNbrFlag": "Y",           // Y = account number available
  "acctFlag": "Y",             // Y = account available
  "comboUnitAccNbrFlagDtoList": []
}
```

### Step 5 — Get Available FTTH Plans
```
POST /ding/custService/qryOfferForShifting
{
  "subsId": "<subsId>",
  "installationAddressId": "<addressId>",
  "offerName": "",             // optional filter
  "pageDto": {"pageIndex": 1, "pageCount": 10}
}
Response: {
  "availableOfferDtoList": [{
    "offerCode": "...",
    "offerName": "FTTH UNLIMITED XXX",
    "offerDesc": "...",
    ...
  }],
  "pageDto": {"currentPage": 1, "pageSize": 10, "totalRecord": N}
}
```

### Step 6 — Submit Shift Order
```
POST /ding/subsService/subsShiftingBsnl
{
  "subsId": "<subsId>",
  "installationAddressId": "<addressId>",
  "offerCode": "<offerCode from Step 5>",
  ...   // additional plan/account fields
}
Response: {
  "orderId": "...",
  "orderStatus": "...",
  "returnCode": "0",
  "returnMsg": "Success"
}
```

---

## Flow 2: VirtualLine → Fixed FTTH Conversion

For subscribers on virtual/VoIP service converting to fixed FTTH.

### Step 1 — Check Conversion Eligibility
```
POST /ding/subsService/changeMainProdCheckBsnl
{"subsId": "<subsId>"}

Response: {
  "changeFlag": "Y",      // Y = can convert
  "accNbrFlag": "Y",
  "acctNbrFlag": "Y",
  "returnCode": "0",
  "returnMsg": "Success"
}
```

### Step 2 — Get Available Plans
```
POST /ding/subsService/qryAvailablePlanListBsnl
{"subsId": "<subsId>", ...}

Response: {planList: [...]}
```

### Step 3 — Submit Conversion Order
```
POST /ding/subsService/changeMainProdBsnl
{
  "subsId": "<subsId>",
  "newOfferCode": "<offerCode>",
  ...
}
```

---

## Flow 3: Cluster-Based Bulk LL→FTTH Migration

For franchise dealers migrating entire exchanges/clusters from copper to fiber.

### Step A — View Pending Migration Clusters
```
POST /ding/lltoftth/qryClusterByCondition
{
  "flag": "N",              // N=pending, Y=accepted
  "franchiseeCode": "307710"
}
Response: {
  "clusterData": [{
    "clusterId": "...",
    "clusterName": "...",
    "exchangeCode": "...",
    "totalSubs": N,
    "pendingSubs": N
  }]
}
```

### Step B — Get Subscribers in Cluster
```
POST /ding/lltoftth/qryGroupByClusterId
{
  "franchiseeCode": "307710",
  "clusterId": "<clusterId>"
}
Response: {
  "clusterData": [{
    "subsId": "...",
    "subsNbr": "0832XXXXXXX",
    "customerName": "...",
    "currentPlan": "...",
    "address": "..."
  }]
}
```

### Step C — Accept/Reject Migration
```
POST /ding/lltoftth/updateFlagByFranchise
{
  "franchiseeCode": "307710",
  "clusterIds": ["clusterId1", "clusterId2"],
  "flag": "Y"   // Y=accept, N=reject
}
Response: {"returnCode": "0", "returnMsg": "Success"}
```

---

## Flow 4: New FTTH Connection (Fresh Install)

### Step 1 — Check if Customer Already Exists
```
POST /ding/custService/checkCustExists
{"mobileNumber": "9XXXXXXXXX"}

Response: {"custId": "..."}  // or null if new customer
```

### Step 2 — Get Available Plans by Address
```
POST /ding/custService/qryOfferListByAddr
{"addressId": "<addressId>", "serviceType": "FIBER_BB"}

Response: {"offerList": [{offerCode, offerName, ...}]}
```

### Step 3 — Create Customer (if new)
```
POST /ding/custService/createCustomerBsnl
{
  "custName": "...",
  "mobile": "9XXXXXXXXX",
  "email": "...",
  "custType": "A",
  ...
}
```

### Step 4 — Create Account
```
POST /ding/custService/createAccountBsnl
{
  "custId": "<custId>",
  "offerCode": "<offerCode>",
  "installationAddressId": "<addressId>",
  ...
}
```

### Step 5 — Submit New Connection Order
```
POST /ding/custService/newConnection
{"custOrder": {
  "custId": "...",
  "offerCode": "...",
  "installationAddressId": "...",
  ...
}}
```

---

## Other Useful Endpoints

### Subscriber Detail
```
POST /ding/subsService/qrySubsDetailBsnl
{"subsId": "<subsId>", "addressFlag": "Y", "subsPlanFlag": "Y"}
```

### Account Service Actions
```
POST /ding/acctService/accountServiceRequestBsnl
```

### Reconnection Check/Execute
```
POST /ding/subsService/reconnectionCheckBsnl
POST /ding/subsService/reconnectionBsnl
{"subsId": "<subsId>"}
```

### Subscriber Termination
```
POST /ding/subsService/terminationBsnl
{"subsId": "<subsId>"}
```

### Trouble Ticket (Fault Report)
```
POST /ding/troubleTicket/saveAndSubmitOrderBsnl
POST /ding/troubleTicket/qryServiceTypeBsnl
POST /ding/troubleTicket/closeOrderBsnl
```

### Number Shifting (MNP-style)
```
POST /ding/subsService/numberShiftingBsnl
POST /ding/subsService/subsTransferCheckBsnl
POST /ding/subsService/subsTransferBsnl
```

---

## Response Format
All responses follow:
```json
{
  "code": "200",          // HTTP-level code
  "message": "success",
  "pageInfo": null,
  "data": {
    "returnCode": "0",    // App-level: "0" = success
    "returnMsg": "Success",
    ...actual data...
  }
}
```

Error codes:
- `returnCode: "0"` = success
- `returnCode: "CC-S-SALES-00001"` = subscriber not found or inactive
- `returnCode: "42001044"` = account not in franchise / SPI error
- `code: "41600024"` = required param null
- `code: "7070001"` = unknown/internal error
