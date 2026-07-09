import { getBackendBaseUrl, getCsrfTokenFromCookie } from "./admin-auth";

const MUTATING_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);

const PROVENANCE_HEADER_NAMES = [
  "x-request-id",
  "x-correlation-id",
  "x-forwarded-for",
  "x-real-ip",
  "cf-connecting-ip",
  "x-forwarded-host",
  "x-forwarded-proto",
  "user-agent",
  "referer",
  "origin",
  "x-keycloak-client",
  "x-auth-flow",
];

export type AdminApiRequestContext = {
  method?: string;
  cookieHeader?: string | null;
  csrfToken?: string | null;
  incomingHeaders?: Headers;
  sourceRoute?: string;
};

export function isMutatingAdminApiMethod(method = "GET") {
  return MUTATING_METHODS.has(method.toUpperCase());
}

export function getAdminApiUrl(pathSegments: string[], search = "") {
  const backendBaseUrl = getBackendBaseUrl();

  if (!backendBaseUrl) {
    return null;
  }

  const normalizedBaseUrl = backendBaseUrl.replace(/\/$/, "");
  const normalizedPath = pathSegments.map(encodeURIComponent).join("/");
  return `${normalizedBaseUrl}/${normalizedPath}${search}`;
}

export function buildAdminApiHeaders({
  method = "GET",
  cookieHeader,
  csrfToken,
  incomingHeaders,
  sourceRoute,
}: AdminApiRequestContext = {}) {
  const headers = new Headers();
  headers.set("x-service-name", "tdp-admin");
  headers.set("x-tdp-admin-proxy", "nextjs");

  if (sourceRoute) {
    headers.set("x-tdp-admin-source-route", sourceRoute);
  }

  if (cookieHeader) {
    headers.set("Cookie", cookieHeader);
  }

  if (isMutatingAdminApiMethod(method)) {
    const token = csrfToken ?? getCsrfTokenFromCookie(cookieHeader ?? null);
    if (token) {
      headers.set("X-CSRFToken", token);
    }
  }

  for (const headerName of PROVENANCE_HEADER_NAMES) {
    const value = incomingHeaders?.get(headerName);
    if (value && !headers.has(headerName)) {
      headers.set(headerName, value);
    }
  }

  if (!headers.has("x-request-id")) {
    headers.set("x-request-id", crypto.randomUUID());
  }

  return headers;
}

export function setAuthenticatedNoStore(headers: Headers) {
  headers.set("Cache-Control", "no-store");
  headers.set("Pragma", "no-cache");
  headers.set("Expires", "0");
  return headers;
}

export async function fetchDjangoAdminApi(
  pathSegments: string[],
  {
    search = "",
    body,
    headers,
    context,
  }: {
    search?: string;
    body?: BodyInit | null;
    headers?: HeadersInit;
    context?: AdminApiRequestContext;
  } = {}
) {
  const url = getAdminApiUrl(pathSegments, search);

  if (!url) {
    throw new Error("NEXT_PUBLIC_BACKEND_URL is not configured.");
  }

  const method = context?.method ?? "GET";
  const requestHeaders = buildAdminApiHeaders(context);
  const extraHeaders = new Headers(headers);

  extraHeaders.forEach((value, key) => {
    requestHeaders.set(key, value);
  });

  return fetch(url, {
    method,
    credentials: "include",
    cache: "no-store",
    headers: requestHeaders,
    body: method === "GET" || method === "HEAD" ? undefined : body,
  });
}
