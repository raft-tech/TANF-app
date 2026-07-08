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

The login and health flows use these environment variables:

- `NEXT_PUBLIC_AUTH_URL`
- `NEXT_PUBLIC_AUTH_BROWSER_URL`
- `NEXT_PUBLIC_BACKEND_URL`

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

The Django backend remains authoritative for session validation and admin
authorization. Next.js route gating is only a user-experience guard.

## Routes

- `/` checks the Django admin session before rendering the admin console.
- `/login` renders the same login page.
- `/logout` redirects through the admin-scoped Django/Keycloak logout flow.
- `/api/backend-health` probes the backend auth endpoint and reports non-2xx responses as failures.
- `/api/admin/*` forwards backend API requests with the Django session cookie
  and CSRF token required by mutating requests.

## Testing

Run the focused admin checks with:

```bash
yarn test
```
