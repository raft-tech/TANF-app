import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

const originalEnv = { ...process.env };

afterEach(() => {
  process.env = { ...originalEnv };
  vi.restoreAllMocks();
});

describe("/api/admin pass-through route", () => {
  it("passes a single-endpoint GET through to Django and disables caching", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        Response.json(
          { results: [{ id: 1, name: "Django-owned response" }] },
          { headers: { "Cache-Control": "public, max-age=60" } }
        )
      )
    );

    const { GET } = await import("./route");
    const response = await GET(
      new NextRequest(
        "https://admin.example.gov/api/admin/test-viewset?page=1",
        {
          headers: {
            cookie: "sessionid=abc",
            "x-request-id": "request-123",
          },
        }
      ),
      { params: Promise.resolve({ path: ["test-viewset"] }) }
    );

    expect(response.status).toBe(200);
    expect(response.headers.get("Cache-Control")).toBe("no-store");
    expect(response.headers.get("Pragma")).toBe("no-cache");
    expect(await response.json()).toEqual({
      results: [{ id: 1, name: "Django-owned response" }],
    });
    expect(fetch).toHaveBeenCalledWith(
      "https://backend.example.gov/v1/test-viewset?page=1",
      expect.objectContaining({
        method: "GET",
        credentials: "include",
        cache: "no-store",
      })
    );

    const [, init] = vi.mocked(fetch).mock.calls[0];
    const headers = new Headers(init?.headers);
    expect(headers.get("Cookie")).toBe("sessionid=abc");
    expect(headers.get("x-request-id")).toBe("request-123");
    expect(headers.get("x-tdp-admin-source-route")).toBe(
      "/api/admin/test-viewset"
    );
  });

  it("forwards CSRF and request provenance for mutating requests", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => Response.json({ ok: true }, { status: 201 }))
    );

    const { POST } = await import("./route");
    const response = await POST(
      new NextRequest("https://admin.example.gov/api/admin/test-viewset", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          cookie: "sessionid=abc; csrftoken=csrf-cookie",
          "x-forwarded-for": "203.0.113.9",
        },
        body: JSON.stringify({ action: "django-owned" }),
      }),
      { params: Promise.resolve({ path: ["test-viewset"] }) }
    );

    expect(response.status).toBe(201);
    expect(response.headers.get("Cache-Control")).toBe("no-store");
    const [, init] = vi.mocked(fetch).mock.calls[0];
    const headers = new Headers(init?.headers);
    expect(init?.body).toBe(JSON.stringify({ action: "django-owned" }));
    expect(headers.get("X-CSRFToken")).toBe("csrf-cookie");
    expect(headers.get("x-forwarded-for")).toBe("203.0.113.9");
    expect(headers.get("content-type")).toBe("application/json");
    expect(headers.get("x-service-name")).toBe("tdp-admin");
    expect(headers.get("x-tdp-admin-proxy")).toBe("nextjs");
  });

  it("returns a no-store configuration error when the backend URL is missing", async () => {
    delete process.env.NEXT_PUBLIC_BACKEND_URL;
    delete process.env.NEXT_PUBLIC_AUTH_URL;

    const { GET } = await import("./route");
    const response = await GET(
      new NextRequest("https://admin.example.gov/api/admin/test-viewset"),
      { params: Promise.resolve({ path: ["test-viewset"] }) }
    );

    expect(response.status).toBe(500);
    expect(response.headers.get("Cache-Control")).toBe("no-store");
    expect(await response.json()).toEqual({
      ok: false,
      error: "NEXT_PUBLIC_BACKEND_URL is not configured.",
    });
  });
});
