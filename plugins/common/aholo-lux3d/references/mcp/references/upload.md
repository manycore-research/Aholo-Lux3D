# Prepare every input through the unified Asset upload

Every image, view, model or other file URL passed into a Aholo Lux3D operation must
come from the unified **Asset token → OUS upload → successful status URL**
flow below. A URL being accessible to the host does not prove Aholo Lux3D's internal
services can read it. Do not pass an arbitrary user URL, attachment URL,
third-party storage URL, data URL or local path directly to a create tool.

## Resolve the input before quoting or creating

| Input available to the host | Required preparation |
| --- | --- |
| Local file or attachment with readable bytes | Upload those bytes through Asset/OUS. |
| External HTTP(S) URL, including a host attachment or third-party upload URL | Fetch the intended file with an available host download tool, then upload the downloaded bytes through Asset/OUS. A page containing an image is not the image file. |
| URL from an earlier successful Asset/OUS upload in this workflow | Reuse only with its successful upload receipt, unchanged input and matching region; re-upload if expired or unusable. A familiar hostname alone is not a receipt. |
| An intermediate generated result used as input to another operation | Apply the same rule: download and upload through Asset/OUS unless a matching successful unified-upload receipt already exists. |
| Text-only request with no file input | No upload is needed. |

Apply this to **each** file input, including all views and all model/material
references. Preserve input order and each input's role. Keep a private mapping
from the original input and full-file MD5 to its completed upload and returned
URL; build quotes and create arguments using those returned URLs. If a URL must
be replaced after quoting, refresh the affected quote for the exact new inputs.
Do not re-upload final output links merely to deliver them to the user; this
requirement applies when a URL becomes an input to another Aholo Lux3D operation.

## Check the actual upload capability

The mapped Connector tools do not include upload. Input preparation may use a host
tool that implements this exact unified Asset/OUS flow, or the host's local
file and HTTPS facilities following the requests below. An unrelated uploader
returning a public URL does not satisfy this requirement. Upload is auxiliary
input preparation; account, quote, generation and task operations still use MCP.

For direct HTTP upload, the host needs file access (and download capability for
remote inputs), hashing, HTTP multipart requests, and secure credential injection
for the China Asset token endpoint. An established MCP connection does **not**
mean its stored key can be read by a command or another HTTP tool. Use supported
host secret injection; never extract the key from private application files,
request it in chat, or place it in command arguments or generated scripts.

If a required capability or credential route is unavailable, explain that
specific gap and preserve the prepared plan. Ask for an accessible file or the
missing host upload configuration as appropriate. **Do not bypass the gap by
passing the original URL to Aholo Lux3D**, and do not switch to an unrelated storage
service. A publicly readable URL still needs this unified upload.

## Regional upload routing

Use the region selected for the MCP task: China Asset base URL is
`https://api.aholo3d.cn`; international Asset base URL is
`https://api.aholo.ai/global`. Thus international token requests use
`https://api.aholo.ai/global/asset/v1/token`, while the international MCP URL is
`https://api.aholo.ai/lux3d-mcp/mcp` (without `/global`). Keep credentials and
upload receipts isolated by region; never reuse a China upload receipt or key
for an international task, or fall back to another region after failure.

## Upload protocol

Use the following flow rather than rediscovering the endpoints for every file.
These fields follow the repository's Asset client; live service acceptance is
separate from package validation. If the service rejects the documented request
shape, resolve that mismatch before continuing instead of guessing parameters.

1. Read the actual, nonempty file. Record its original filename and size in
   **bytes**, and compute the **whole-file MD5 as a hexadecimal string before
   sending the upload**. Do not use a filename hash or an individual part's hash.
   Keep the file bytes unchanged through upload.
2. Call `GET <selected-region Asset base URL>/asset/v1/token` with that region's API Key as the
   raw `Authorization` header, without `Bearer`. This is the same regional key
   used by MCP, not a separately issued upload credential. Check the success response and
   obtain `ousToken`, HTTPS `globalDomain` and positive integer `blockSize` from
   its data object (`d` when wrapped). The token belongs to this upload; do not
   reuse it for a different file. Use the returned domain and threshold, never
   a hard-coded OUS hostname or a fixed "5 MB" rule.
3. For requests in the table, send only the temporary
   `ous-token-v2: <ousToken>` credential to the returned OUS origin. **Never send
   the Aholo Lux3D API Key to OUS, a source URL, a download URL or a redirected origin.**
   Let the HTTP client generate multipart boundaries.

| Condition / stage | Request relative to `globalDomain` | Fields |
| --- | --- | --- |
| `size <= blockSize` | `POST /ous/api/v2/single/upload` | Multipart file `file`; form field `md5` = whole-file MD5. |
| `size > blockSize`: initialize | `POST /ous/api/v2/block/upload/init` | Form fields `md5`, `blocks = ceil(size / blockSize)`, `size` in bytes, `name` = original filename. |
| Send each missing part | `POST /ous/api/v2/block/upload/part` | Multipart file `file`; form field `block` = **1-based** part index. |
| Check completion | `GET /ous/api/v2/upload/status` | Same `ous-token-v2` header; status is associated with that token. |

For a single upload, `md5` is a separate form field alongside `file`; sending
only the file is incomplete. The packaged protocol does not put it in the JSON
body or require a query parameter. A "missing md5" rejection is a request-shape
problem: inspect the actual form construction and field name before retrying.

For a block upload, split at the returned `blockSize`. The last part may be
shorter. If initialization says `deduplicated: true`, proceed to status. Otherwise
upload `lackBlocks`, expanding ranges such as `1-3,5` into valid indexes within
`1..blocks`; empty or omitted `lackBlocks` means all parts in this client flow.
Send parts sequentially. Do not invent a separate merge/complete request.

For every Asset/OUS response, check HTTP success and then the business envelope.
When `c` is present, `0` or `"0"` indicates success; a nonzero code is a failure
even with HTTP 200. Use `m` as a diagnostic after redacting sensitive values,
then read the data object from `d`. If the endpoint returns a direct data object,
read that object instead. For example, `{"c":"0","d":{"status":5,"url":"https://…"}}`
has its upload status inside `d`; `{"c":"12","m":"…"}` is not a successful
upload. Do not confuse business code `c` with upload state `status`.

After the single request or all required parts complete, poll status using the
same token. Record any returned `taskId` or `obsTaskId` as upload diagnostics;
these are **not** Aholo Lux3D generation task IDs. Neither ID is an extra status query
parameter in this flow. Only `status = 5` with a real HTTP(S) `url` means success.
Statuses `6` and `8` mean failure. Intermediate IDs, progress and `uploadKey`
alone do not prove completion; never construct a URL from them.

Use bounded requests (30 seconds each) and a bounded status wait (normally one
second between checks, at most two minutes overall). Stop on a terminal failure.
A timeout leaves the upload uncertain: retain its token in private transient
state and reconcile that upload before starting another. Read-only requests
may be retried up to three attempts within the time budget. Do not blindly
repeat upload POSTs or acquire new tokens in a retry loop. If a request was
explicitly rejected before acceptance, correct the proven validation error
before retrying; do not treat an ambiguous timeout as such a rejection.

## Return to the MCP workflow

Use the exact successful status `url` in each corresponding MCP input field.
Retain the upload receipt and input mapping privately for reuse and recovery:
original input reference, role/order, whole-file MD5, region, successful status,
returned URL and completion time. An upload task ID is useful when returned.
The URL is an input/output of the workflow, not a diagnostic log field;
do not save raw token responses in user deliverables or print keys/tokens in
logs. Delete temporary source copies when no longer needed, without deleting
the user's originals. On upload failure, report the stage and safe error code;
do not present an intermediate or original URL as ready for generation.

Uploading prepares a file; it neither creates a 3D task nor authorizes additional
paid steps. Preserve the user's intended subject. Do not silently remove people,
redesign the reference, or add image-generation steps to solve an upload issue.
If a transformation is actually needed, explain it and apply the existing
[planning](planning.md) and [review](review.md) rules to that changed scope.
