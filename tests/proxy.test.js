import test from "node:test";
import assert from "node:assert/strict";
import proxy from "../platform/proxy.js";
test("old browser pages redirect to the one login origin; ingestion keeps method, body and authentication", async () => {
  let received;
  const env = {
    CANONICAL_HOST: "apps.zwart.my.id",
    PRODUCT: "daily-apps",
    BACKEND: {
      fetch: async (request) => {
        received = request;
        return Response.json({ ok: true });
      },
    },
  };
  const redirect = await proxy.fetch(
    new Request("https://aquapure-app.zwart.qzz.io/?invite=real-token"),
    env,
  );
  assert.equal(redirect.status, 301);
  assert.equal(
    redirect.headers.get("Location"),
    "https://apps.zwart.my.id/?invite=real-token",
  );
  const oldCanonical = await proxy.fetch(
    new Request("https://daily-apps-app.zwart.qzz.io/?form=public-link"), env,
  );
  assert.equal(oldCanonical.status, 301);
  assert.equal(oldCanonical.headers.get("Location"), "https://apps.zwart.my.id/?form=public-link");
  const result = await proxy.fetch(
    new Request("https://aquapure-app.zwart.qzz.io/api/ingest", {
      method: "POST",
      headers: {
        Authorization: "Bearer private-device-key",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ph: 7.1 }),
    }),
    env,
  );
  assert.equal(result.status, 200);
  assert.equal(received.method, "POST");
  assert.equal(
    received.headers.get("Authorization"),
    "Bearer private-device-key",
  );
  assert.equal(received.headers.get("X-Zwart-Product"), "daily-apps");
  assert.deepEqual(await received.json(), { ph: 7.1 });
});
