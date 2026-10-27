import test from "node:test";
import assert from "node:assert/strict";
import worker from "../platform/worker.js";
import { testEnv } from "./adapter.js";
import { PRODUCTS } from "../platform/definitions.js";
const origin = "https://single-workspace.test";
async function call(
  env,
  path,
  method = "GET",
  data,
  auth = {},
  product = "daily-apps",
) {
  const headers = {
    "Content-Type": "application/json",
    "X-Zwart-Product": product,
    "X-App-Origin": origin,
    Origin: origin,
    "CF-Connecting-IP": "isolated-test",
  };
  if (auth.cookie) headers.Cookie = auth.cookie;
  if (auth.csrf) headers["X-CSRF-Token"] = auth.csrf;
  const response = await worker.fetch(
    new Request(origin + "/api" + path, {
      method,
      headers,
      body: data === undefined ? undefined : JSON.stringify(data),
    }),
    env,
  );
  return {
    status: response.status,
    data: await response.json(),
    cookie: response.headers.get("Set-Cookie")?.split(";")[0],
  };
}
async function account(env, email = "owner@isolated.test") {
  const r = await call(env, "/auth/register", "POST", {
    name: "Isolated owner",
    email,
    password: "isolated-password-12345",
  });
  assert.equal(r.status, 201);
  return { ...r.data, cookie: r.cookie };
}
async function root(env, a) {
  const r = await call(
    env,
    "/workspaces",
    "POST",
    { name: "One real workspace" },
    a,
  );
  assert.equal(r.status, 201);
  return r.data.workspace.id;
}
async function area(env, a, id, kind) {
  const r = await call(env, `/workspaces/${id}/areas/${kind}`, "POST", {}, a);
  assert.equal(r.status, 200, JSON.stringify(r.data));
  return r.data.workspace.id;
}
async function create(env, a, id, kind, data, product = "daily-apps") {
  const r = await call(
    env,
    `/workspaces/${id}/records/${kind}`,
    "POST",
    data,
    a,
    product,
  );
  assert.equal(r.status, 201, JSON.stringify(r.data));
  return r.data.record;
}
test("one cookie reaches every preserved area; equal kind names remain isolated inside one visible workspace", async () => {
  const env = testEnv(),
    auth = await account(env),
    id = await root(env, auth),
    seen = new Map();
  for (const [product, spec] of Object.entries(PRODUCTS)) {
    const ws =
      product === "daily-apps" ? id : await area(env, auth, id, product);
    const records = {};
    let pending = spec.modules.filter(
      (m) =>
        !m.tool &&
        !["focus_sessions", "attempts", "form_responses"].includes(m.key),
    );
    while (pending.length) {
      let progressed = false;
      for (const m of [...pending]) {
        if (
          m.fields.some(
            (f) => f.type === "ref" && f.required && !records[f.ref],
          )
        )
          continue;
        const data = { status: m.statuses[0] };
        for (const f of m.fields) {
          if (f.type === "ref") {
            if (records[f.ref]) data[f.key] = records[f.ref].id;
            continue;
          }
          if (f.type === "items") {
            data[f.key] = [{ product_id: records.products.id, quantity: 1 }];
            continue;
          }
          if (f.type === "quiz") {
            data[f.key] = [
              {
                question: "Arithmetic validation",
                options: ["2", "3"],
                correct: 0,
              },
            ];
            continue;
          }
          if (f.type === "json") {
            data[f.key] =
              m.key === "forms"
                ? [{ label: "Input", type: "text", required: true }]
                : [];
            continue;
          }
          if (f.type === "select") {
            data[f.key] = f.options[0];
            continue;
          }
          if (f.type === "number") {
            data[f.key] = Math.max(f.min ?? 1, 1);
            continue;
          }
          if (f.type === "money") {
            data[f.key] = 10000;
            continue;
          }
          if (f.type === "date") {
            data[f.key] = new Date().toISOString().slice(0, 10);
            continue;
          }
          if (f.type === "datetime") {
            data[f.key] = new Date(
              Date.now() + (f.key === "end" ? 7200000 : 3600000),
            ).toISOString();
            continue;
          }
          if (f.type === "time") {
            data[f.key] = "09:00";
            continue;
          }
          if (f.type === "email") {
            data[f.key] = "test@isolated.test";
            continue;
          }
          if (f.type === "url") {
            data[f.key] = "https://example.invalid/";
            continue;
          }
          if (f.type === "color") {
            data[f.key] = "#123456";
            continue;
          }
          data[f.key] =
            f.key === "sku"
              ? "isolated-" + product
              : f.key === "path"
                ? "src/isolated.js"
                : f.key === "name"
                  ? "Isolated " + product + " " + m.key
                  : "Isolated input";
        }
        const row = await create(env, auth, ws, m.key, data);
        records[m.key] = row;
        seen.set(product + ":" + m.key, row);
        pending = pending.filter((x) => x !== m);
        progressed = true;
        // Test fixture exercises >100 distinct forms; rate-limit behavior is covered separately.
        env.DB.sqlite.exec("DELETE FROM rate_limits");
      }
      assert.ok(progressed, "Reference graph has an unresolved dependency");
    }
  }
  assert.ok(seen.size > 90);
  const session = await call(env, "/auth/session", "GET", undefined, auth);
  assert.equal(session.data.workspaces.length, 1);
  const exported = await call(
    env,
    `/workspaces/${id}/export`,
    "GET",
    undefined,
    auth,
  );
  assert.equal(exported.data.records.length, seen.size);
  assert.equal(new Set(exported.data.records.map((r) => r.area)).size, 11);
  const media = seen.get("renderforge:projects"),
    code = seen.get("codeforgeme:projects");
  assert.notEqual(media.workspace_id, code.workspace_id);
  assert.equal(
    (
      await call(
        env,
        `/workspaces/${media.workspace_id}/records/projects/${code.id}`,
        "GET",
        undefined,
        auth,
      )
    ).status,
    404,
  );
});
test("role changes and removal on the root take effect across previously active child sessions", async () => {
  const env = testEnv(),
    owner = await account(env),
    id = await root(env, owner),
    child = await area(env, owner, id, "daganghub"),
    editor = await account(env, "editor@isolated.test");
  const invited = await call(
    env,
    `/workspaces/${id}/invitations`,
    "POST",
    { email: editor.user.email, role: "editor" },
    owner,
  );
  const token = new URL(invited.data.url).searchParams.get("invite");
  assert.equal(
    (await call(env, "/invitations/accept", "POST", { token }, editor)).status,
    200,
  );
  await create(env, editor, child, "customers", {
    name: "Actual test customer",
  });
  assert.equal(
    (
      await call(
        env,
        `/workspaces/${child}/members`,
        "PATCH",
        { id: editor.user.id, role: "viewer" },
        owner,
      )
    ).status,
    403,
  );
  await call(
    env,
    `/workspaces/${id}/members`,
    "PATCH",
    { id: editor.user.id, role: "viewer" },
    owner,
  );
  assert.equal(
    (
      await call(
        env,
        `/workspaces/${child}/records/customers`,
        "POST",
        { name: "Blocked" },
        editor,
      )
    ).status,
    403,
  );
  assert.equal(
    (
      await call(
        env,
        `/workspaces/${child}/records/customers`,
        "GET",
        undefined,
        editor,
      )
    ).status,
    200,
  );
  await call(
    env,
    `/workspaces/${id}/members/${editor.user.id}`,
    "DELETE",
    undefined,
    owner,
  );
  assert.equal(
    (
      await call(
        env,
        `/workspaces/${child}/records/customers`,
        "GET",
        undefined,
        editor,
      )
    ).status,
    404,
  );
});
test("cross-area work is connected to projects; focus duration is server-computed and task completion is idempotent", async () => {
  const env = testEnv(),
    a = await account(env),
    id = await root(env, a),
    child = await area(env, a, id, "daganghub");
  const p = await create(env, a, id, "projects", { name: "Deliver real work" }),
    task = await create(env, a, id, "tasks", {
      name: "Finish work",
      date: new Date().toISOString().slice(0, 10),
      project_id: p.id,
    });
  const customer = await create(env, a, child, "customers", {
    name: "Customer",
  });
  assert.equal(
    (
      await call(
        env,
        `/workspaces/${id}/projects/${p.id}/links`,
        "POST",
        { record_id: customer.id },
        a,
      )
    ).status,
    200,
  );
  const focus = await call(
    env,
    `/workspaces/${id}/focus/start`,
    "POST",
    { task_id: task.id },
    a,
  );
  assert.equal(focus.status, 201);
  assert.equal(
    (await call(env, `/workspaces/${id}/focus/start`, "POST", {}, a)).status,
    409,
  );
  assert.equal(
    (
      await call(
        env,
        `/workspaces/${id}/records/focus_sessions`,
        "POST",
        { name: "Forged", seconds: 999 },
        a,
      )
    ).status,
    403,
  );
  const row = focus.data.record;
  env.DB.sqlite
    .prepare(
      "UPDATE records SET data=json_set(data,'$.started_at',?) WHERE id=?",
    )
    .run(new Date(Date.now() - 120000).toISOString(), row.id);
  const stopped = await call(
    env,
    `/workspaces/${id}/focus/stop`,
    "POST",
    { id: row.id, complete_task: true, seconds: 99999 },
    a,
  );
  assert.equal(stopped.status, 200);
  assert.ok(
    stopped.data.record.data.seconds >= 120 &&
      stopped.data.record.data.seconds < 123,
  );
  assert.equal(
    (await call(env, `/workspaces/${id}/focus/stop`, "POST", { id: row.id }, a))
      .data.idempotent,
    true,
  );
  const hub = (
    await call(
      env,
      `/workspaces/${id}/projects/${p.id}/hub`,
      "GET",
      undefined,
      a,
    )
  ).data;
  assert.equal(hub.progress.done, 1);
  assert.equal(hub.links.length, 1);
  assert.ok(hub.focus_seconds >= 120);
  assert.equal(
    (
      await call(
        env,
        `/workspaces/${id}/records/projects/${p.id}`,
        "DELETE",
        undefined,
        a,
      )
    ).status,
    409,
  );
});
test("project links cannot reference another team and search/export never cross workspace boundaries", async () => {
  const env = testEnv(),
    a = await account(env),
    id = await root(env, a),
    other = await account(env, "other@isolated.test"),
    otherId = await root(env, other);
  const p = await create(env, a, id, "projects", {
      name: "Visible team project",
    }),
    foreign = await create(env, other, otherId, "projects", {
      name: "Private foreign project",
    });
  assert.equal(
    (
      await call(
        env,
        `/workspaces/${id}/projects/${p.id}/links`,
        "POST",
        { record_id: foreign.id },
        a,
      )
    ).status,
    404,
  );
  const search = await call(
    env,
    `/workspaces/${id}/hub/search?q=Private`,
    "GET",
    undefined,
    a,
  );
  assert.deepEqual(search.data.records, []);
  assert.equal(
    (await call(env, `/workspaces/${otherId}/hub`, "GET", undefined, a)).status,
    404,
  );
});
test("legacy import preserves record IDs, payloads, owner and exact membership, and cannot be stolen", async () => {
  const env = testEnv(),
    a = await account(env),
    legacy = await call(
      env,
      "/workspaces",
      "POST",
      { name: "Existing media" },
      a,
      "renderforge",
    );
  const old = legacy.data.workspace.id;
  const r = await create(
    env,
    a,
    old,
    "projects",
    { name: "Existing actual record" },
    "renderforge",
  );
  const before = env.DB.sqlite
    .prepare("SELECT data FROM records WHERE id=?")
    .get(r.id).data;
  const outsider = await account(env, "stranger@isolated.test");
  assert.equal(
    (await call(env, "/import-legacy", "POST", { id: old }, outsider)).status,
    404,
  );
  const imported = await call(env, "/import-legacy", "POST", { id: old }, a);
  assert.equal(imported.status, 200);
  assert.equal(
    (await call(env, "/import-legacy", "POST", { id: old }, a)).data.workspace
      .id,
    imported.data.workspace.id,
  );
  assert.equal(
    env.DB.sqlite.prepare("SELECT data FROM records WHERE id=?").get(r.id).data,
    before,
  );
  assert.equal(
    (
      await call(
        env,
        `/workspaces/${old}/records/projects/${r.id}`,
        "GET",
        undefined,
        a,
      )
    ).data.record.id,
    r.id,
  );
  assert.equal(
    (
      await call(
        env,
        `/workspaces/${imported.data.workspace.id}/export`,
        "GET",
        undefined,
        a,
      )
    ).data.records[0].id,
    r.id,
  );
});
test("global trash restores child-area records without weakening root permissions", async () => {
  const env = testEnv(),
    a = await account(env),
    id = await root(env, a),
    child = await area(env, a, id, "daganghub"),
    c = await create(env, a, child, "customers", { name: "Recoverable" });
  assert.equal(
    (
      await call(
        env,
        `/workspaces/${child}/records/customers/${c.id}`,
        "DELETE",
        undefined,
        a,
      )
    ).status,
    200,
  );
  assert.equal(
    (await call(env, `/workspaces/${id}/trash`, "GET", undefined, a)).data
      .records[0].id,
    c.id,
  );
  assert.equal(
    (await call(env, `/workspaces/${id}/restore/${c.id}`, "POST", {}, a))
      .status,
    200,
  );
  assert.equal(
    (await call(env, `/workspaces/${id}/trash`, "GET", undefined, a)).data
      .records.length,
    0,
  );
});
test("a new account receives one visible empty workspace with every tool enabled and a unified agenda", async () => {
  const env = testEnv(),
    a = await account(env),
    id = await root(env, a);
  assert.equal(
    (await call(env, "/auth/session", "GET", undefined, a)).data.workspaces
      .length,
    1,
  );
  assert.equal(
    (await call(env, `/workspaces/${id}/areas`, "GET", undefined, a)).data
      .areas &&
      env.DB.sqlite.prepare("SELECT count(*) AS n FROM workspace_areas").get()
        .n,
    10,
  );
  assert.equal(
    (await call(env, `/workspaces/${id}/export`, "GET", undefined, a)).data
      .records.length,
    0,
  );
  const business = await area(env, a, id, "daganghub");
  await create(env, a, business, "expenses", {
    name: "Isolated purchase",
    amount: 10000,
    date: "2026-10-27",
    status: "active",
  });
  await create(env, a, id, "tasks", {
    name: "Isolated dated task",
    date: "2026-10-27",
    status: "todo",
  });
  const agenda = await call(
    env,
    `/workspaces/${id}/hub/agenda?month=2026-10`,
    "GET",
    undefined,
    a,
  );
  assert.equal(agenda.status, 200);
  assert.ok(agenda.data.events.some((e) => e.area === "daganghub"));
  assert.ok(agenda.data.events.some((e) => e.area === "daily-apps"));
  const board = await call(
    env,
    `/workspaces/${id}/hub/tasks`,
    "GET",
    undefined,
    a,
  );
  assert.equal(board.data.records.length, 1);
  assert.equal(board.data.records[0].kind, "tasks");
});
test("focus history can be removed and restored, while active timers cannot be removed", async () => {
  const env = testEnv(),
    a = await account(env),
    id = await root(env, a);
  const start = await call(env, `/workspaces/${id}/focus/start`, "POST", {}, a);
  const key = start.data.record.id;
  assert.equal(
    (
      await call(
        env,
        `/workspaces/${id}/records/focus_sessions/${key}`,
        "DELETE",
        undefined,
        a,
      )
    ).status,
    409,
  );
  await call(env, `/workspaces/${id}/focus/stop`, "POST", { id: key }, a);
  assert.equal(
    (
      await call(
        env,
        `/workspaces/${id}/records/focus_sessions/${key}`,
        "DELETE",
        undefined,
        a,
      )
    ).status,
    200,
  );
  assert.equal(
    (await call(env, `/workspaces/${id}/restore/${key}`, "POST", {}, a)).status,
    200,
  );
  const read = await call(
    env,
    `/workspaces/${id}/records/focus_sessions/${key}`,
    "GET",
    undefined,
    a,
  );
  assert.equal(read.data.record.status, "done");
});
