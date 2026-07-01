export type BackendHealth = {
  ok: boolean;
  backendUrl: string | null;
  authCheckUrl: string | null;
  status?: number;
  statusText?: string;
  error?: string;
};

export type AdminSession = {
  authenticated: boolean;
  authorized?: boolean;
  csrf?: string;
  user?: {
    email?: string;
    first_name?: string;
    last_name?: string;
    roles?: string[];
  };
  detail?: string;
};

export function getBackendBaseUrl() {
  return (
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    process.env.NEXT_PUBLIC_AUTH_URL ||
    null
  );
}

export function getAuthBaseUrl() {
  const authUrl = process.env.NEXT_PUBLIC_AUTH_URL;

  if (authUrl) {
    return authUrl.replace(/\/$/, "");
  }

  const backendUrl = getBackendBaseUrl();

  if (!backendUrl) {
    return null;
  }

  return backendUrl.replace(/\/v1\/?$/, "").replace(/\/$/, "");
}

export function getBrowserAuthBaseUrl() {
  return (
    process.env.NEXT_PUBLIC_AUTH_BROWSER_URL?.replace(/\/$/, "") ??
    getAuthBaseUrl()
  );
}

export function getAdminAuthBaseUrl() {
  const authBaseUrl = getAuthBaseUrl();

  if (!authBaseUrl) {
    return null;
  }

  return `${authBaseUrl}/admin-auth`;
}

export function getBrowserAdminAuthBaseUrl() {
  const authBaseUrl = getBrowserAuthBaseUrl();

  if (!authBaseUrl) {
    return null;
  }

  return `${authBaseUrl}/admin-auth`;
}

export function getLoginUrl(provider: "dotgov" | "ams") {
  const authBaseUrl = getAuthBaseUrl();

  if (!authBaseUrl) {
    return null;
  }

  return `${authBaseUrl}/login/${provider}`;
}

export function getAdminLoginUrl(provider: "dotgov" | "ams", nextUrl?: string) {
  const adminAuthBaseUrl = getBrowserAdminAuthBaseUrl();

  if (!adminAuthBaseUrl) {
    return null;
  }

  const loginUrl = new URL(`${adminAuthBaseUrl}/login/${provider}`);
  if (nextUrl) {
    loginUrl.searchParams.set("next", nextUrl);
  }
  return loginUrl.toString();
}

export function getAdminAuthCheckUrl() {
  const adminAuthBaseUrl = getAdminAuthBaseUrl();
  return adminAuthBaseUrl ? `${adminAuthBaseUrl}/auth_check` : null;
}

export function getAdminLogoutUrl() {
  const adminAuthBaseUrl = getBrowserAdminAuthBaseUrl();
  return adminAuthBaseUrl ? `${adminAuthBaseUrl}/logout/oidc` : null;
}

export function getProviderLoginPath(provider: "dotgov" | "ams") {
  return `/login/${provider}`;
}

export function getAdminProviderLoginPath(provider: "dotgov" | "ams") {
  return `/login/${provider}`;
}

export function getCsrfTokenFromCookie(cookieHeader: string | null) {
  const match = cookieHeader?.match(/(?:^|;\s*)csrftoken=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : null;
}

export function buildAdminRequestHeaders({
  cookieHeader,
  csrfToken,
  includeCsrf = false,
  headers = {},
}: {
  cookieHeader?: string | null;
  csrfToken?: string | null;
  includeCsrf?: boolean;
  headers?: HeadersInit;
}) {
  const requestHeaders = new Headers(headers);
  requestHeaders.set("x-service-name", "tdp-admin");

  if (cookieHeader) {
    requestHeaders.set("Cookie", cookieHeader);
  }

  if (includeCsrf) {
    const token = csrfToken ?? getCsrfTokenFromCookie(cookieHeader ?? null);
    if (token) {
      requestHeaders.set("X-CSRFToken", token);
    }
  }

  return requestHeaders;
}

export async function checkAdminSession(cookieHeader?: string | null): Promise<AdminSession> {
  const adminAuthCheckUrl = getAdminAuthCheckUrl();

  if (!adminAuthCheckUrl) {
    return { authenticated: false, detail: "Admin auth URL is not configured." };
  }

  try {
    const response = await fetch(adminAuthCheckUrl, {
      method: "GET",
      credentials: "include",
      cache: "no-store",
      headers: buildAdminRequestHeaders({ cookieHeader }),
    });
    const data = (await response.json().catch(() => ({}))) as AdminSession;

    if (!response.ok) {
      return {
        ...data,
        authenticated: Boolean(data.authenticated),
        authorized: Boolean(data.authorized),
        detail: data.detail ?? `Admin auth check returned ${response.status}`,
      };
    }

    return data;
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return { authenticated: false, detail: message };
  }
}

export async function checkBackendHealth(): Promise<BackendHealth> {
  const backendUrl = getBackendBaseUrl();

  if (!backendUrl) {
    return {
      ok: false,
      backendUrl: null,
      authCheckUrl: null,
      error: "NEXT_PUBLIC_BACKEND_URL is not set. Check your environment variables.",
    };
  }

  const normalizedBackendUrl = backendUrl.replace(/\/$/, "");
  const authCheckUrl = `${normalizedBackendUrl}/auth_check`;

  try {
    const response = await fetch(authCheckUrl, {
      method: "GET",
      credentials: "include",
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
    });

    return {
      ok: response.ok,
      backendUrl: normalizedBackendUrl,
      authCheckUrl,
      status: response.status,
      statusText: response.statusText,
      error: response.ok
        ? undefined
        : `Backend auth check returned ${response.status} ${response.statusText}`,
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);

    return {
      ok: false,
      backendUrl: normalizedBackendUrl,
      authCheckUrl,
      error: message,
    };
  }
}
