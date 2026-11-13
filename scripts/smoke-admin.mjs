import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { createServer } from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const appDirectory = path.resolve(process.argv[2] || path.join(repoRoot, "tdp-admin"));
const backendRequests = [];
const backend = createServer((request, response) => {
  backendRequests.push(request.url);
  response.setHeader("Content-Type", "application/json");
  response.end(JSON.stringify({ authenticated: false }));
});
backend.listen(0, "127.0.0.1");
await once(backend, "listening");

const portReservation = createServer();
portReservation.listen(0, "127.0.0.1");
await once(portReservation, "listening");
const port = portReservation.address().port;
await new Promise((resolve) => portReservation.close(resolve));

const backendOrigin = `http://127.0.0.1:${backend.address().port}`;
const appOrigin = `http://127.0.0.1:${port}`;
const publicOrigin = "https://admin.example.gov";
const app = spawn(process.execPath, [
  path.join(appDirectory, "node_modules/next/dist/bin/next"), "start", "--hostname", "127.0.0.1",
], {
  cwd: appDirectory,
  env: {
    ...process.env,
    NODE_ENV: "production",
    PORT: String(port),
    ADMIN_AUTH_URL: backendOrigin,
    ADMIN_AUTH_BROWSER_URL: publicOrigin,
    ADMIN_BACKEND_URL: `${backendOrigin}/admin-api/v1`,
    ADMIN_FRONTEND_ORIGIN: publicOrigin,
    ADMIN_API_PROXY_TOKEN: "smoke-test-only-token",
  },
  stdio: ["ignore", "pipe", "pipe"],
});
let logs = "";
app.stdout.on("data", (chunk) => { logs += chunk; });
app.stderr.on("data", (chunk) => { logs += chunk; });
const request = (route) => fetch(`${appOrigin}${route}`, {
  redirect: "manual", signal: AbortSignal.timeout(5000),
});

try {
  let ready = false;
  for (let attempt = 0; attempt < 60; attempt++) {
    if (app.exitCode !== null) throw new Error(`Admin exited with ${app.exitCode}`);
    try {
      const health = await request("/api/health");
      assert.equal(health.status, 200);
      assert.deepEqual(await health.json(), { ok: true });
      ready = true;
      break;
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 250));
    }
  }
  assert.ok(ready, "Admin must listen on the runtime PORT");

  const login = await request("/login");
  assert.equal(login.status, 200);
  assert.match(await login.text(), /Sign in to TANF Admin/);

  const redirect = await request("/login/ams?next=https://untrusted.example/");
  assert.equal(redirect.status, 307);
  const location = new URL(redirect.headers.get("location"));
  assert.equal(location.origin, publicOrigin);
  assert.equal(location.pathname, "/admin-auth/login/ams");
  assert.equal(location.searchParams.get("next"), `${publicOrigin}/dashboard`);

  const health = await request("/api/backend-health");
  assert.equal(health.status, 200);
  assert.equal((await health.json()).ok, true);
  assert.ok(backendRequests.includes("/admin-auth/auth_check"));

  const users = await request("/users");
  if (users.status === 307) {
    assert.equal(new URL(users.headers.get("location"), appOrigin).pathname, "/login");
  } else {
    // Suspense may flush the loading page before Next.js emits its redirect.
    assert.equal(users.status, 200);
    assert.match(
      await users.text(),
      /<meta(?=[^>]*http-equiv="refresh")(?=[^>]*content="\d+;url=\/login")[^>]*>/,
    );
  }
  console.log("Admin production smoke checks passed: runtime PORT/URLs, login, health, and anonymous access.");
} catch (error) {
  console.error(logs);
  throw error;
} finally {
  app.kill("SIGTERM");
  backend.closeAllConnections();
  backend.close();
}
