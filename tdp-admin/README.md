# TDP Admin

Administrative frontend for the TANF Data Portal.

## Getting Started

Install dependencies and start the app with the workspace task or a local dev server.

```bash
corepack prepare yarn@4.6.0 --activate
yarn install
yarn dev
```

Open [http://localhost:3001](http://localhost:3001) to reach the admin login page.

## Environment

Copy `.env.example` to `.env` for Docker Compose, or `.env.local` for
`yarn dev`, then adjust values for your backend.

The login and health flows use these environment variables:

- `NEXT_PUBLIC_AUTH_URL`
- `NEXT_PUBLIC_AUTH_BROWSER_URL`
- `NEXT_PUBLIC_BACKEND_URL`
- `ADMIN_BACKEND_URL`
- `ADMIN_FRONTEND_ORIGIN`
- `ADMIN_API_PROXY_TOKEN`

`NEXT_PUBLIC_AUTH_URL` should point to the Django auth origin. When it is not
set, the app derives the auth origin from `NEXT_PUBLIC_BACKEND_URL`.
When the admin app runs in Docker, set `NEXT_PUBLIC_AUTH_URL` to the
container-reachable Django origin and `NEXT_PUBLIC_AUTH_BROWSER_URL` to the
browser-reachable Django origin, for example:

```bash
NEXT_PUBLIC_AUTH_URL=http://host.docker.internal:8989
NEXT_PUBLIC_AUTH_BROWSER_URL=http://localhost:8989
```

The backend auth service should expose admin-scoped routes under
`/admin-auth`:

- `/admin-auth/login/dotgov`
- `/admin-auth/login/ams`
- `/admin-auth/auth_check`
- `/admin-auth/logout/oidc`

Admin API proxy requests use the Django backend's admin-only API prefix:

- `/admin-api/v1/*`

When `ADMIN_BACKEND_URL` is not set, the app derives it from
`NEXT_PUBLIC_BACKEND_URL` by replacing `/v1` with `/admin-api/v1`.
`ADMIN_API_PROXY_TOKEN` must match the Django backend's
`ADMIN_API_PROXY_TOKEN`; the Next.js server sends it to Django for
`/admin-api/v1/*` requests.
`ADMIN_FRONTEND_ORIGIN` must match the browser origin of the admin app, such as
`http://localhost:3001` locally or `https://admin.tanfdata.acf.hhs.gov` in
production. The `/api/admin/*` proxy rejects mutating requests when the request
`Origin` does not match this value, and it forwards CSRF only from the
`X-CSRFToken` request header.

The Django backend remains authoritative for session validation and admin
authorization. Next.js route gating is only a user-experience guard.
Django also validates `/admin-api/v1/*` requests before API handlers run; the
Next.js proxy only forwards request context and the server-side proxy token.

## Routes

- `/` checks the Django admin session before rendering the admin console.
- `/login` renders the same login page.
- `/logout` redirects through the admin-scoped Django logout flow.
- `/api/backend-health` probes the backend auth endpoint and reports non-2xx responses as failures.
- `/api/admin/*` forwards backend API requests with the Django session cookie,
  CSRF token required by mutating requests, and server-side proxy token to
  `/admin-api/v1/*`.

## Testing

Run the focused admin checks with:

```bash
yarn test
```
