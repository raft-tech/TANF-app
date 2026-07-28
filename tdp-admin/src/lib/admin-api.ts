import {
  buildAdminRequestHeaders,
  getAdminBackendBaseUrl,
} from "./admin-auth";

const MUTATING_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);
const BODYLESS_METHODS = new Set(["GET", "HEAD"]);

export type AdminApiRequestOptions = {
  method?: string;
  search?: string;
  body?: BodyInit | null;
  cookieHeader?: string | null;
  csrfToken?: string | null;
  headers?: HeadersInit;
  sourceRoute?: string;
  requestId?: string | null;
};

export function isMutatingAdminApiMethod(method = "GET") {
  return MUTATING_METHODS.has(method.toUpperCase());
}

export function getAdminApiUrl(pathSegments: string[], search = "") {
  const backendBaseUrl = getAdminBackendBaseUrl();

  if (!backendBaseUrl) {
    return null;
  }

  const normalizedBaseUrl = backendBaseUrl.replace(/\/$/, "");
  const normalizedPath = pathSegments.map(encodeURIComponent).join("/");
  return `${normalizedBaseUrl}/${normalizedPath}${search}`;
}

export function setAuthenticatedNoStore(headers: Headers) {
  headers.set("Cache-Control", "no-store");
  headers.set("Pragma", "no-cache");
  headers.set("Expires", "0");
  return headers;
}

export async function requestAdminApi(
  pathSegments: string[],
  {
    method = "GET",
    search = "",
    body,
    cookieHeader,
    csrfToken,
    headers = {},
    sourceRoute,
    requestId,
  }: AdminApiRequestOptions = {}
) {
  const url = getAdminApiUrl(pathSegments, search);

  if (!url) {
    throw new Error(
      "ADMIN_BACKEND_URL or NEXT_PUBLIC_BACKEND_URL is not configured."
    );
  }

  const adminProxyToken = process.env.ADMIN_API_PROXY_TOKEN;

  if (!adminProxyToken) {
    throw new Error("ADMIN_API_PROXY_TOKEN is not configured.");
  }

  const normalizedMethod = method.toUpperCase();
  const requestHeaders = buildAdminRequestHeaders({
    cookieHeader,
    csrfToken,
    includeCsrf: isMutatingAdminApiMethod(normalizedMethod),
    headers,
  });
  requestHeaders.set("X-Admin-Proxy-Token", adminProxyToken);
  requestHeaders.set("X-Request-ID", requestId || crypto.randomUUID());

  if (sourceRoute) {
    requestHeaders.set("X-TDP-Admin-Source-Route", sourceRoute);
  }

  return fetch(url, {
    method: normalizedMethod,
    credentials: "include",
    cache: "no-store",
    headers: requestHeaders,
    body: BODYLESS_METHODS.has(normalizedMethod) ? undefined : body,
  });
}

type ReadAdminResourceOptions = Omit<
  AdminApiRequestOptions,
  "method" | "body"
>;

export const adminApi = {
  dataFiles: {
    list: (options?: ReadAdminResourceOptions) =>
      requestAdminApi(["data_files"], options),
    get: (id: string | number, options?: ReadAdminResourceOptions) =>
      requestAdminApi(["data_files", String(id)], options),
  },
};
