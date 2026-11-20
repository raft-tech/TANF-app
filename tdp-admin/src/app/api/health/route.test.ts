import { expect, it, vi } from "vitest";
import { GET } from "./route";

it("reports liveness without depending on the backend", async () => {
  const fetch = vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("offline"));
  try {
    const response = GET();
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ ok: true });
    expect(response.headers.get("Cache-Control")).toBe("no-store");
    expect(fetch).not.toHaveBeenCalled();
  } finally {
    fetch.mockRestore();
  }
});
