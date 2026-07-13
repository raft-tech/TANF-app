import { NextRequest, NextResponse } from "next/server";
import {
  buildAdminRequestHeaders,
  getAdminBackendBaseUrl,
  getCsrfTokenFromCookie,
} from "@/lib/admin-auth";

const MUTATING_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);

function getBackendUrl(pathSegments: string[], search: string) {
  const backendBaseUrl = getAdminBackendBaseUrl();

  if (!backendBaseUrl) {
    return null;
  }

  const normalizedBaseUrl = backendBaseUrl.replace(/\/$/, "");
  const normalizedPath = pathSegments.map(encodeURIComponent).join("/");
  return `${normalizedBaseUrl}/${normalizedPath}${search}`;
}

async function proxyAdminRequest(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const { path } = await context.params;
  const backendUrl = getBackendUrl(path, request.nextUrl.search);

  if (!backendUrl) {
    return NextResponse.json(
      {
        ok: false,
        error: "ADMIN_BACKEND_URL or NEXT_PUBLIC_BACKEND_URL is not configured.",
      },
      { status: 500 }
    );
  }

  const adminProxyToken = process.env.ADMIN_API_PROXY_TOKEN;

  if (!adminProxyToken) {
    return NextResponse.json(
      {
        ok: false,
        error: "ADMIN_API_PROXY_TOKEN is not configured.",
      },
      { status: 500 }
    );
  }

  const cookieHeader = request.headers.get("cookie");
  const csrfToken =
    request.headers.get("X-CSRFToken") ?? getCsrfTokenFromCookie(cookieHeader);
  const headers = buildAdminRequestHeaders({
    cookieHeader,
    csrfToken,
    includeCsrf: MUTATING_METHODS.has(request.method),
  });
  const contentType = request.headers.get("content-type");

  if (contentType) {
    headers.set("content-type", contentType);
  }
  headers.set("X-Admin-Proxy-Token", adminProxyToken);

  const response = await fetch(backendUrl, {
    method: request.method,
    credentials: "include",
    cache: "no-store",
    headers,
    body:
      request.method === "GET" || request.method === "HEAD"
        ? undefined
        : await request.text(),
  });

  return new NextResponse(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: response.headers,
  });
}

export const GET = proxyAdminRequest;
export const POST = proxyAdminRequest;
export const PUT = proxyAdminRequest;
export const PATCH = proxyAdminRequest;
export const DELETE = proxyAdminRequest;
