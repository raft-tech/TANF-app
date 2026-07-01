import { afterEach, describe, expect, it } from "vitest";

const originalEnv = { ...process.env };

afterEach(() => {
  process.env = { ...originalEnv };
});

describe("login redirect routes", () => {
  it("redirects Login.gov requests through the auth host", async () => {
    process.env.NEXT_PUBLIC_AUTH_URL = "https://auth.example.gov";

    const { GET } = await import("./dotgov/route");
    const response = GET(new Request("https://admin.example.gov/login/dotgov"));

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe(
      "https://auth.example.gov/admin-auth/login/dotgov"
    );
  });

  it("redirects ACF AMS requests through the auth host", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    delete process.env.NEXT_PUBLIC_AUTH_URL;

    const { GET } = await import("./ams/route");
    const response = GET(
      new Request("https://admin.example.gov/login/ams?next=https%3A%2F%2Fadmin.example.gov%2F")
    );

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe(
      "https://backend.example.gov/admin-auth/login/ams?next=https%3A%2F%2Fadmin.example.gov%2F"
    );
  });
});
