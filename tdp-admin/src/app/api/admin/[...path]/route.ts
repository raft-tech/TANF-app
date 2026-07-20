import { NextRequest, NextResponse } from "next/server";
import {
  buildAdminRequestHeaders,
  getAdminBackendBaseUrl,
} from "@/lib/admin-auth";

const MUTATING_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);

function normalizeOrigin(origin: string) {
  return new URL(origin).origin;
}

function getBackendUrl(pathSegments: string[], search: string) {
  const backendBaseUrl = getAdminBackendBaseUrl();

  if (!backendBaseUrl) {
    return null;
  }

  const normalizedBaseUrl = backendBaseUrl.replace(/\/$/, "");
  const normalizedPath = pathSegments.map(encodeURIComponent).join("/");
  return `${normalizedBaseUrl}/${normalizedPath}${search}`;
}

function getExpectedAdminOrigin() {
  const expectedOrigin = process.env.ADMIN_FRONTEND_ORIGIN;

  if (!expectedOrigin) {
    return null;
  }

  try {
    return normalizeOrigin(expectedOrigin);
  } catch {
    return null;
  }
}

function validateMutatingRequest(request: NextRequest) {
  const expectedOrigin = getExpectedAdminOrigin();

  if (!expectedOrigin) {
    return {
      response: NextResponse.json(
        {
          ok: false,
          error: "ADMIN_FRONTEND_ORIGIN is not configured.",
        },
        { status: 500 }
      ),
      csrfToken: null,
    };
  }

  const origin = request.headers.get("origin");

  if (!origin) {
    return {
      response: NextResponse.json(
        {
          ok: false,
          error: "Origin header is required for admin API mutations.",
        },
        { status: 403 }
      ),
      csrfToken: null,
    };
  }

  try {
    if (normalizeOrigin(origin) !== expectedOrigin) {
      return {
        response: NextResponse.json(
          {
            ok: false,
            error: "Origin is not allowed for admin API mutations.",
          },
          { status: 403 }
        ),
        csrfToken: null,
      };
    }
  } catch {
    return {
      response: NextResponse.json(
        {
          ok: false,
          error: "Origin header is invalid.",
        },
        { status: 403 }
      ),
      csrfToken: null,
    };
  }

  const csrfToken = request.headers.get("X-CSRFToken")?.trim();

  if (!csrfToken) {
    return {
      response: NextResponse.json(
        {
          ok: false,
          error: "X-CSRFToken header is required for admin API mutations.",
        },
        { status: 403 }
      ),
      csrfToken: null,
    };
  }

  return { response: null, csrfToken };
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

  const isMutatingRequest = MUTATING_METHODS.has(request.method);
  const mutatingRequestValidation = isMutatingRequest
    ? validateMutatingRequest(request)
    : { response: null, csrfToken: null };

  if (mutatingRequestValidation.response) {
    return mutatingRequestValidation.response;
  }

  const cookieHeader = request.headers.get("cookie");
  const headers = buildAdminRequestHeaders({
    cookieHeader,
    csrfToken: mutatingRequestValidation.csrfToken,
    includeCsrf: isMutatingRequest,
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
