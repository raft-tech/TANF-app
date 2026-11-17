# Authenticate to the TDP API

Use this guide to sign in with OpenID Connect (OIDC), obtain an access token,
and call the [DataFile submission API](data_files.md). OIDC identifies the user;
the API still checks that user's TDP approval, role, and State, Territory, or
Tribe (STT) access on every request.

## Before you start

Ask your TDP administrator or [TDP support](mailto:tanfdata@acf.hhs.gov) for:

- An active, approved TDP account with the permissions needed for your integration.
- The API base URL for your environment, including `https://` but excluding `/v1`.
- The public OIDC issuer URL and confirmation that external API access is enabled.
  The issuer normally ends in `/realms/tdp`. It can use a different hostname from
  the API. Use the public issuer, not an internal server address.
- Your numeric STT ID and the reporting programs and years you may submit.

Sign in with the same identity you use for TDP: Login.gov for grantees or AMS for
ACF staff. Accounts with an `@acf.hhs.gov` email address must use AMS.

The examples use a web browser, a Bash-compatible terminal, and **curl**, a free
command-line HTTP client. Check availability with `curl --version`. Windows users
can use a Bash terminal such as WSL; the shell syntax below is not PowerShell
syntax. The device-flow example also uses Python 3 (`python3 --version`) to
generate PKCE values and read JSON. No Postman, paid software, or additional
Python packages are required.

## Obtain an access token with a browser and curl

TDP uses Keycloak to connect to Login.gov and AMS. The public API client is
`tdp-cli`; it does not require a client secret. The device authorization flow
lets you sign in using a browser on this computer or another device.

### 1. Set your environment URLs

Replace these example hostnames with the values supplied for your environment.
Keep the API and identity provider in the same environment.

```bash
export API_BASE_URL='https://your-tdp-host.example.org'
export OIDC_ISSUER='https://your-identity-host.example.org/realms/tdp'
export CLIENT_ID='tdp-cli'
```

Find the provider's endpoints in its discovery document:

```bash
curl --silent --show-error --fail \
  "$OIDC_ISSUER/.well-known/openid-configuration"
```

Use its `device_authorization_endpoint` and `token_endpoint` values. For TDP's
Keycloak provider they normally have these paths:

```bash
export DEVICE_ENDPOINT="$OIDC_ISSUER/protocol/openid-connect/auth/device"
export TOKEN_ENDPOINT="$OIDC_ISSUER/protocol/openid-connect/token"
```

### 2. Request a device code

The following examples save sensitive responses in your current directory.
Work in a private directory outside source control. `umask 077` restricts new
files to your user on systems that support Unix file permissions.

The `tdp-cli` client requires PKCE with the `S256` method for device authorization.
Generate a random verifier and its SHA-256 challenge before requesting a device
code. Keep the verifier private and use the same terminal through step 3: the
token exchange must send the original verifier. Generate a new pair only when
starting a new device authorization request.

```bash
umask 077
export CODE_VERIFIER=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
CODE_CHALLENGE=$(python3 - <<'PY'
import base64
import hashlib
import os

digest = hashlib.sha256(os.environ["CODE_VERIFIER"].encode("ascii")).digest()
print(base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii"))
PY
)
```

Now, request the device code

```bash
curl --silent --show-error --fail \
  --request POST "$DEVICE_ENDPOINT" \
  --data-urlencode "client_id=$CLIENT_ID" \
  --data-urlencode 'scope=openid email profile tdp-user-attributes' \
  --data-urlencode 'code_challenge_method=S256' \
  --data-urlencode "code_challenge=$CODE_CHALLENGE" \
  --output device.json
cat device.json
```

`Missing parameter: code_challenge_method` means the request omitted the PKCE
method. Adding the method alone is insufficient: send the matching challenge
above and the verifier in step 3. If you lost the verifier, restart step 2.

Illustrative response (codes and expiration values vary):

```json
{
  "device_code": "REDACTED_DEVICE_CODE",
  "user_code": "ABCD-EFGH",
  "verification_uri": "https://your-identity-host.example.org/realms/tdp/device",
  "verification_uri_complete": "https://your-identity-host.example.org/realms/tdp/device?user_code=ABCD-EFGH",
  "expires_in": 600,
  "interval": 5
}
```

Open `verification_uri_complete` in your browser. Alternatively, open
`verification_uri` and enter `user_code`. Check that the displayed code matches,
sign in through Login.gov or AMS, complete any required multifactor authentication,
and approve the request. Only approve a request you initiated.

### 3. Exchange the device code for tokens

Set `DEVICE_CODE` to the `device_code` from step 2. If Python 3 is available:

```bash
DEVICE_CODE=$(python3 -c 'import json; print(json.load(open("device.json"))["device_code"])')
```

Otherwise, assign the returned value yourself with `DEVICE_CODE='returned-value'`.
Keep the device code private; it is different from the short code entered in the
browser.

Wait at least the returned `interval` (seconds) between token requests. If omitted,
use five seconds. Run this request after approving in the browser:

```bash
curl --silent --show-error \
  --request POST "$TOKEN_ENDPOINT" \
  --data-urlencode "client_id=$CLIENT_ID" \
  --data-urlencode 'grant_type=urn:ietf:params:oauth:grant-type:device_code' \
  --data-urlencode "device_code=$DEVICE_CODE" \
  --data-urlencode "code_verifier=$CODE_VERIFIER" \
  --output tokens.json \
  --write-out 'HTTP %{http_code}\n'
```

On HTTP `200`, the JSON contains `access_token`, `token_type`, and `expires_in`;
it may also contain `refresh_token`, `refresh_expires_in`, and `id_token`.
Do not print or share the token response. On an error status, inspect `tokens.json`:

| OAuth error | What to do |
| --- | --- |
| `authorization_pending` | Finish signing in; wait the interval and repeat the token request. |
| `slow_down` | Add five seconds to the polling interval for this and subsequent attempts. |
| `access_denied` | Stop; the authorization was denied. |
| `expired_token` | Stop and request a new device code. |

Automated clients should stop when the device code expires, increase the delay
on connection timeouts, and stop on other errors. See the
[device authorization standard](https://www.rfc-editor.org/rfc/rfc8628.html#section-3.5)
for polling behavior.

### 4. Send the access token to the API

After a successful token response, load **`access_token`** into a shell variable:

```bash
export ACCESS_TOKEN=$(python3 -c 'import json; print(json.load(open("tokens.json"))["access_token"])')
export STT_ID='123'

curl --silent --show-error --fail \
  --header "Authorization: Bearer $ACCESS_TOKEN" \
  --header 'Accept: application/json' \
  "$API_BASE_URL/v1/data_files/?stt=$STT_ID"
```

Replace `123` with your actual numeric STT ID. Without Python, read the response
locally and set `ACCESS_TOKEN` to its `access_token` value; avoid entering secrets
in a terminal that records command history. Send the token in the HTTP
`Authorization` header on **every** API request, including downloads. Use the
access token, not the ID token or refresh token. Never put tokens in URLs.

The bearer token must be issued for `tdp-cli` and include the Django API audience
(default `tdp-django`). TDP's client configuration supplies that audience. Tokens
from another client or directly from Login.gov/AMS are not interchangeable with
these tokens. Browser session cookies are not needed for these examples.

## Token expiration and refresh

Use `expires_in` from the token response to schedule renewal; do not assume a
fixed lifetime. If a refresh token was returned and is still valid:

```bash
REFRESH_TOKEN=$(python3 -c 'import json; print(json.load(open("tokens.json"))["refresh_token"])')
curl --silent --show-error \
  --request POST "$TOKEN_ENDPOINT" \
  --data-urlencode "client_id=$CLIENT_ID" \
  --data-urlencode 'grant_type=refresh_token' \
  --data-urlencode "refresh_token=$REFRESH_TOKEN" \
  --output refreshed-tokens.json \
  --write-out 'HTTP %{http_code}\n'
```

Only after HTTP `200`, replace the stored token response with the new response
and load its new `access_token`. Retain the newest refresh token when returned;
rotation and expiration depend on environment policy. On `invalid_grant` or an
expired/revoked refresh token, repeat device sign-in. Do not keep retrying an
invalid refresh token.

These tokens act on behalf of the signed-in person. The public `tdp-cli` client
does not support password grants or client-credentials service accounts. An
integration must allow a person to sign in again when renewal is no longer
possible; coordinate requirements for unattended access with TDP support.

Treat access and refresh tokens as credentials. Protect stored tokens with your
system's credential storage, keep them out of logs and repositories, and use
HTTPS. Delete the example response files and unset token variables when finished.

## Alternative for applications: authorization code with PKCE

Applications that can receive an approved redirect can use authorization code
with PKCE instead of device authorization:

1. Obtain an allowed redirect URI from your TDP administrator. Generate a random
   `state` and PKCE `code_verifier`; derive its SHA-256, base64url-encoded
   `code_challenge` without padding.
2. Open the discovered `authorization_endpoint` with `response_type=code`,
   `client_id=tdp-cli`, the redirect URI, the same scopes used above, `state`,
   `code_challenge`, and `code_challenge_method=S256`.
3. Complete browser sign-in. At the callback, verify `state` matches the original
   request, then exchange the returned code at `token_endpoint` using
   `grant_type=authorization_code`, `client_id`, `code`, the exact same
   `redirect_uri`, and `code_verifier`. No client secret is needed.
4. Use the resulting access token and refresh process as described above.

Use an OAuth/OIDC library that supports PKCE when implementing this flow.

## Legacy administrator tokens

The older `/v1/security/get-token` endpoint is a separate mechanism restricted to
activated OFA System Admin users after browser sign-in. Those tokens use
`Authorization: Token <token>` and default to a 24-hour lifetime (configurable by
the deployment). This endpoint does not issue OIDC bearer tokens. Use the OIDC
flow above for user integrations.
