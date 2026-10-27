import { PRODUCTS } from "./definitions.js";
import { session, equal, uid, limit } from "./auth.js";
import {
  fail,
  body,
  access,
  getRecord,
  deleteRecord,
  present,
  auditStatement,
} from "./data.js";

export const AREAS = {
  "daily-apps": { name: "Rencana & kebiasaan", group: "Harian" },
  daganghub: { name: "Usaha & keuangan", group: "Operasi" },
  renderforge: { name: "Media & publikasi", group: "Studio" },
  tutormind: { name: "Belajar & kuis", group: "Belajar" },
  servora: { name: "Layanan & perjalanan", group: "Operasi" },
  aquapure: { name: "Lapangan & sensor", group: "Operasi" },
  "clinic-os": { name: "Klinik", group: "Operasi" },
  "legalbot-garuda": { name: "Perkara & dokumen", group: "Operasi" },
  codeforgeme: { name: "Kode & pengujian", group: "Studio" },
  gridcraft: { name: "Level & shader", group: "Studio" },
  stockgenie: { name: "Pasar & portofolio", group: "Operasi" },
};
const json = (data, status = 200) =>
  Response.json(data, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
const scope =
  "(r.workspace_id=? OR r.workspace_id IN (SELECT workspace_id FROM workspace_areas WHERE root_id=?))";
const complete = new Set([
  "done",
  "completed",
  "paid",
  "graded",
  "resolved",
  "published",
]);
async function authorize(request, env, write = false) {
  const user = await session(env, request);
  if (!user) fail(401, "Masuk terlebih dahulu.");
  if (write) {
    if (request.headers.get("origin") !== request.headers.get("X-App-Origin"))
      fail(403, "Origin tidak valid.");
    if (!equal(request.headers.get("X-CSRF-Token"), user.csrf))
      fail(403, "Session berubah. Muat ulang halaman.");
  }
  if (!(await limit(env, "hub:" + user.id, write ? 100 : 300, 60)))
    fail(429, "Terlalu banyak request. Tunggu sebentar.");
  return user;
}
async function rootAccess(env, user, id, write = false, owner = false) {
  return access(env, user, id, "daily-apps", write, owner);
}
async function areas(env, root) {
  const a = await env.DB.prepare(
    "SELECT area,workspace_id FROM workspace_areas WHERE root_id=?",
  )
    .bind(root)
    .all();
  return Object.fromEntries([
    ["daily-apps", root],
    ...a.results.map((x) => [x.area, x.workspace_id]),
  ]);
}
async function ensureArea(env, user, root, area) {
  const ws = await rootAccess(env, user, root, true);
  if (!AREAS[area]) fail(404, "Bidang kerja tidak dikenal.");
  if (area === "daily-apps") return ws;
  const existing = await env.DB.prepare(
    "SELECT workspace_id FROM workspace_areas WHERE root_id=? AND area=?",
  )
    .bind(root, area)
    .first();
  if (existing)
    return {
      id: existing.workspace_id,
      name: ws.name,
      product: area,
      role: ws.role,
      root_id: root,
    };
  const id = uid(),
    now = Date.now();
  try {
    await env.DB.batch([
      env.DB.prepare(
        "INSERT INTO workspaces(id,product,name,owner_id,created_at) VALUES(?,?,?,?,?)",
      ).bind(id, area, ws.name, ws.owner_id, now),
      env.DB.prepare(
        "INSERT INTO workspace_areas(root_id,area,workspace_id,created_at) VALUES(?,?,?,?)",
      ).bind(root, area, id, now),
      env.DB.prepare(
        "INSERT INTO members(workspace_id,user_id,role) SELECT ?,user_id,role FROM members WHERE workspace_id=?",
      ).bind(id, root),
      auditStatement(env, root, user, "area.enable", id, area),
    ]);
  } catch (error) {
    const winner = await env.DB.prepare(
      "SELECT workspace_id FROM workspace_areas WHERE root_id=? AND area=?",
    )
      .bind(root, area)
      .first();
    if (!winner) throw error;
    return {
      id: winner.workspace_id,
      name: ws.name,
      product: area,
      role: ws.role,
      root_id: root,
    };
  }
  return { id, name: ws.name, product: area, role: ws.role, root_id: root };
}
export async function importLegacyWorkspace(env, user, id) {
  const old = await env.DB.prepare(
    "SELECT * FROM workspaces WHERE id=? AND owner_id=?",
  )
    .bind(id, user.id)
    .first();
  if (!old || !AREAS[old.product]) fail(404, "Ruang lama tidak ditemukan.");
  if (old.product === "daily-apps")
    return { id: old.id, name: old.name, product: "daily-apps", role: "owner" };
  const linked = await env.DB.prepare(
    "SELECT w.* FROM workspace_areas a JOIN workspaces w ON w.id=a.root_id WHERE a.workspace_id=?",
  )
    .bind(id)
    .first();
  if (linked)
    return {
      id: linked.id,
      name: linked.name,
      product: "daily-apps",
      role: "owner",
    };
  const root = uid(),
    now = Date.now();
  await env.DB.batch([
    env.DB.prepare(
      "INSERT INTO workspaces(id,product,name,owner_id,created_at) VALUES(?,'daily-apps',?,?,?)",
    ).bind(root, old.name, old.owner_id, now),
    env.DB.prepare(
      "INSERT INTO members(workspace_id,user_id,role) SELECT ?,user_id,role FROM members WHERE workspace_id=?",
    ).bind(root, id),
    env.DB.prepare(
      "INSERT INTO workspace_areas(root_id,area,workspace_id,created_at) VALUES(?,?,?,?)",
    ).bind(root, old.product, id, now),
    auditStatement(env, root, user, "workspace.import", id, old.product),
  ]);
  return { id: root, name: old.name, product: "daily-apps", role: "owner" };
}
async function summary(env, root, user, today) {
  const rows = (
    await env.DB.prepare(
      `SELECT r.id,r.workspace_id,r.kind,r.title,r.status,r.data,r.created_at,r.updated_at,w.product AS area FROM records r JOIN workspaces w ON w.id=r.workspace_id WHERE ${scope} AND r.deleted_at IS NULL ORDER BY r.updated_at DESC LIMIT 5001`,
    )
      .bind(root, root)
      .all()
  ).results;
  const truncated = rows.length > 5000;
  rows.length = Math.min(rows.length, 5000);
  const counts = (
    await env.DB.prepare(
      `SELECT w.product AS area,r.kind,r.status,count(*) AS count FROM records r JOIN workspaces w ON w.id=r.workspace_id WHERE ${scope} AND r.deleted_at IS NULL GROUP BY w.product,r.kind,r.status`,
    )
      .bind(root, root)
      .all()
  ).results;
  const total = counts.reduce((n, r) => n + r.count, 0),
    done = counts
      .filter((r) => complete.has(r.status))
      .reduce((n, r) => n + r.count, 0);
  const recent = rows.slice(0, 10).map(({ data, ...r }) => r);
  today = /^\d{4}-\d{2}-\d{2}$/.test(today || "")
    ? today
    : new Date().toISOString().slice(0, 10);
  const tasks = rows
    .filter((r) => r.area === "daily-apps" && r.kind === "tasks")
    .map((r) => ({ ...r, data: JSON.parse(r.data) }));
  const due = tasks
    .filter(
      (r) =>
        !complete.has(r.status) &&
        r.data.date &&
        r.data.date.slice(0, 10) <= today,
    )
    .slice(0, 12);
  const projects = rows
    .filter((r) => r.area === "daily-apps" && r.kind === "projects")
    .map((r) => ({ ...r, data: JSON.parse(r.data) }));
  const focus = rows.find(
    (r) =>
      r.kind === "focus_sessions" &&
      r.status === "active" &&
      JSON.parse(r.data).user_id === user.id,
  );
  return {
    total,
    done,
    counts,
    recent,
    due,
    projects,
    focus: focus ? { ...focus, data: JSON.parse(focus.data) } : null,
    truncated,
    today,
    areas: await areas(env, root),
  };
}
function moduleFor(row) {
  return PRODUCTS[row.area]?.modules.find((m) => m.key === row.kind && !m.tool);
}
async function agenda(env, root, month) {
  if (
    !/^\d{4}-\d{2}$/.test(month) ||
    !Number.isFinite(Date.parse(month + "-01"))
  )
    fail(422, "Bulan tidak valid.");
  const dateKeys = [
    ...new Set(
      Object.values(PRODUCTS).flatMap((p) =>
        p.modules.flatMap((m) =>
          (m.fields || [])
            .filter((f) => ["date", "datetime"].includes(f.type))
            .map((f) => f.key),
        ),
      ),
    ),
  ];
  const dates = dateKeys
    .map((k) => "json_extract(r.data,'$." + k + "') LIKE ?")
    .join(" OR ");
  const rows = (
    await env.DB.prepare(
      `SELECT r.id,r.workspace_id,r.kind,r.title,r.status,r.data,w.product AS area FROM records r JOIN workspaces w ON w.id=r.workspace_id WHERE ${scope} AND r.deleted_at IS NULL AND (${dates}) ORDER BY r.updated_at DESC LIMIT 1001`,
    )
      .bind(root, root, ...dateKeys.map(() => month + "%"))
      .all()
  ).results;
  const truncated = rows.length > 1000;
  rows.length = Math.min(rows.length, 1000);
  const events = rows.flatMap((row) => {
    const data = JSON.parse(row.data),
      module = moduleFor(row);
    return (module?.fields || [])
      .filter(
        (f) =>
          ["date", "datetime"].includes(f.type) &&
          typeof data[f.key] === "string" &&
          data[f.key].startsWith(month),
      )
      .map((f) => ({
        id: row.id,
        workspace_id: row.workspace_id,
        kind: row.kind,
        area: row.area,
        title: row.title,
        status: row.status,
        date: data[f.key],
        label: f.label,
      }));
  });
  return {
    events: events.sort((a, b) => a.date.localeCompare(b.date)),
    truncated,
    month,
  };
}
async function projectHub(env, root, id) {
  const project = await getRecord(env, root, id, "projects");
  const tasks = (
    await env.DB.prepare(
      "SELECT * FROM records WHERE workspace_id=? AND kind='tasks' AND deleted_at IS NULL AND json_extract(data,'$.project_id')=? ORDER BY created_at",
    )
      .bind(root, id)
      .all()
  ).results.map((r) => ({ ...r, data: JSON.parse(r.data) }));
  const links = (
    await env.DB.prepare(
      `SELECT r.id,r.workspace_id,r.kind,r.title,r.status,r.updated_at,w.product AS area FROM workspace_project_links l JOIN records r ON r.id=l.record_id JOIN workspaces w ON w.id=r.workspace_id WHERE l.root_id=? AND l.project_id=? AND r.deleted_at IS NULL AND (r.workspace_id=? OR EXISTS(SELECT 1 FROM workspace_areas a WHERE a.root_id=? AND a.workspace_id=r.workspace_id)) ORDER BY l.created_at DESC`,
    )
      .bind(root, id, root, root)
      .all()
  ).results;
  const focus = await env.DB.prepare(
    "SELECT coalesce(sum(json_extract(data,'$.seconds')),0) AS seconds FROM records WHERE workspace_id=? AND kind='focus_sessions' AND status='done' AND deleted_at IS NULL AND json_extract(data,'$.project_id')=?",
  )
    .bind(root, id)
    .first();
  return {
    project,
    tasks,
    links,
    focus_seconds: focus.seconds,
    progress: {
      total: tasks.length,
      done: tasks.filter((t) => t.status === "done").length,
    },
  };
}
async function startFocus(env, user, root, input) {
  let task = null,
    project = null;
  if (input.task_id) task = await getRecord(env, root, input.task_id, "tasks");
  const projectId = input.project_id || task?.data.project_id || "";
  if (projectId) project = await getRecord(env, root, projectId, "projects");
  if (
    task &&
    projectId &&
    task.data.project_id &&
    task.data.project_id !== projectId
  )
    fail(422, "Tugas berasal dari proyek lain.");
  const id = uid(),
    now = Date.now(),
    data = {
      name: task?.title || project?.title || "Sesi fokus",
      project_id: projectId,
      task_id: task?.id || "",
      user_id: user.id,
      started_at: new Date(now).toISOString(),
      ended_at: "",
      seconds: 0,
    };
  try {
    await env.DB.batch([
      env.DB.prepare(
        "INSERT INTO records(id,workspace_id,kind,title,status,data,created_at,updated_at) VALUES(?,?,'focus_sessions',?,'active',?,?,?)",
      ).bind(id, root, data.name, JSON.stringify(data), now, now),
      auditStatement(env, root, user, "focus.start", id),
    ]);
  } catch (error) {
    if (/unique|constraint/i.test(error.message))
      fail(409, "Masih ada sesi fokus aktif. Selesaikan sesi itu dahulu.");
    throw error;
  }
  return { record: await getRecord(env, root, id) };
}
async function stopFocus(env, user, root, input) {
  const current = await getRecord(env, root, input.id, "focus_sessions");
  if (current.data.user_id !== user.id)
    fail(403, "Sesi fokus ini milik pengguna lain.");
  if (current.status === "done") return { record: current, idempotent: true };
  if (current.status !== "active") fail(409, "Sesi tidak aktif.");
  const now = Date.now(),
    seconds = Math.max(
      0,
      Math.floor((now - Date.parse(current.data.started_at)) / 1000),
    );
  const data = {
    ...current.data,
    seconds,
    ended_at: new Date(now).toISOString(),
  };
  const statements = [
    env.DB.prepare(
      "UPDATE records SET status='done',data=?,updated_at=?,version=version+1 WHERE id=? AND workspace_id=? AND version=? AND status='active'",
    ).bind(JSON.stringify(data), now, current.id, root, current.version),
    env.DB.prepare(
      "INSERT INTO workflow_keys(workspace_id,action,idempotency_key,result,created_at,valid) VALUES(?,'focus.stop',?,?,?,CASE WHEN changes()=1 THEN 1 ELSE 0 END)",
    ).bind(root, current.id, JSON.stringify({ seconds }), now),
  ];
  if (input.complete_task && current.data.task_id) {
    const task = await getRecord(env, root, current.data.task_id, "tasks");
    statements.push(
      env.DB.prepare(
        "UPDATE records SET status='done',updated_at=?,version=version+1 WHERE id=? AND workspace_id=? AND version=?",
      ).bind(now, task.id, root, task.version),
    );
    statements.push(
      env.DB.prepare(
        "INSERT INTO workflow_keys(workspace_id,action,idempotency_key,result,created_at,valid) VALUES(?,'focus.task',?,'{}',?,CASE WHEN changes()=1 THEN 1 ELSE 0 END)",
      ).bind(root, current.id, now),
    );
  }
  statements.push(
    auditStatement(
      env,
      root,
      user,
      "focus.stop",
      current.id,
      String(seconds) + " detik",
    ),
  );
  try {
    await env.DB.batch(statements);
  } catch (error) {
    if (/constraint|unique/i.test(error.message))
      fail(409, "Data berubah. Muat ulang sesi fokus.");
    throw error;
  }
  return { record: await getRecord(env, root, current.id) };
}

export async function unifiedRouter(request, env, legacy) {
  const url = new URL(request.url),
    method = request.method,
    path = url.pathname;
  const canonical = request.headers.get("X-Zwart-Product") === "daily-apps";
  if (canonical && path === "/api/health") {
    await env.DB.prepare("SELECT count(*) AS n FROM workspace_areas").first();
    return json({
      ok: true,
      version: "3.0.0",
      product: "daily-apps",
      application: "Daily Workspace",
      storage: "D1",
      single_origin: true,
    });
  }
  if (canonical && path === "/api/config")
    return json({
      product: PRODUCTS["daily-apps"],
      areas: AREAS,
      version: "3.0.0",
    });
  if (canonical && path === "/api/workspaces" && method === "POST") {
    const user = await authorize(request, env, true),
      input = await body(request);
    if (
      typeof input.name !== "string" ||
      !input.name.trim() ||
      input.name.length > 100
    )
      fail(422, "Nama workspace wajib diisi.");
    const count = await env.DB.prepare(
      "SELECT count(*) AS n FROM workspaces WHERE owner_id=? AND product='daily-apps'",
    )
      .bind(user.id)
      .first();
    if (count.n >= 20) fail(409, "Maksimum 20 workspace per akun.");
    const root = uid(),
      now = Date.now(),
      name = input.name.trim(),
      enabled = { "daily-apps": root };
    const statements = [
      env.DB.prepare(
        "INSERT INTO workspaces(id,product,name,owner_id,created_at) VALUES(?,'daily-apps',?,?,?)",
      ).bind(root, name, user.id, now),
      env.DB.prepare(
        "INSERT INTO members(workspace_id,user_id,role) VALUES(?,?,'owner')",
      ).bind(root, user.id),
    ];
    for (const area of Object.keys(AREAS).filter((a) => a !== "daily-apps")) {
      const child = uid();
      enabled[area] = child;
      statements.push(
        env.DB.prepare(
          "INSERT INTO workspaces(id,product,name,owner_id,created_at) VALUES(?,?,?,?,?)",
        ).bind(child, area, name, user.id, now),
      );
      statements.push(
        env.DB.prepare(
          "INSERT INTO members(workspace_id,user_id,role) VALUES(?,?,'owner')",
        ).bind(child, user.id),
      );
      statements.push(
        env.DB.prepare(
          "INSERT INTO workspace_areas(root_id,area,workspace_id,created_at) VALUES(?,?,?,?)",
        ).bind(root, area, child, now),
      );
    }
    statements.push(auditStatement(env, root, user, "workspace.create", null));
    await env.DB.batch(statements);
    return json(
      {
        workspace: { id: root, name, product: "daily-apps", role: "owner" },
        areas: enabled,
      },
      201,
    );
  }
  if (canonical && path === "/api/ingest") {
    const headers = new Headers(request.headers);
    headers.set("X-Zwart-Product", "aquapure");
    return legacy(new Request(request, { headers }), env);
  }
  if (canonical && path === "/api/legacy-workspaces" && method === "GET") {
    const user = await authorize(request, env);
    const rows = await env.DB.prepare(
      "SELECT w.id,w.name,w.product,m.role FROM workspaces w JOIN members m ON m.workspace_id=w.id WHERE m.user_id=? AND w.product<>'daily-apps' AND NOT EXISTS(SELECT 1 FROM workspace_areas a WHERE a.workspace_id=w.id)",
    )
      .bind(user.id)
      .all();
    return json({ workspaces: rows.results.filter((w) => AREAS[w.product]) });
  }
  if (canonical && path === "/api/import-legacy" && method === "POST") {
    const user = await authorize(request, env, true),
      input = await body(request);
    return json({
      workspace: await importLegacyWorkspace(env, user, input.id),
    });
  }
  const match = path.match(/^\/api\/workspaces\/([^/]+)(?:\/(.*))?$/);
  if (!match) return legacy(request, env);
  const id = match[1],
    route = match[2] || "",
    mutating = !["GET", "HEAD"].includes(method);
  const stored = await env.DB.prepare(
    "SELECT product FROM workspaces WHERE id=?",
  )
    .bind(id)
    .first();
  if (!stored) return legacy(request, env);
  if (stored.product !== "daily-apps") {
    const linked = await env.DB.prepare(
      "SELECT root_id FROM workspace_areas WHERE workspace_id=?",
    )
      .bind(id)
      .first();
    if (!linked) {
      if (canonical)
        fail(404, "Ruang lama belum dihubungkan. Impor melalui pengaturan.");
      return legacy(request, env);
    }
    const user = await authorize(request, env, mutating),
      root = await rootAccess(
        env,
        user,
        linked.root_id,
        mutating && route !== "actions/submit-quiz",
      );
    if (
      (!route && mutating) ||
      (/^(members|invitations)(\/|$)/.test(route) && mutating)
    )
      fail(403, "Kelola nama dan anggota melalui pengaturan workspace utama.");
    const member = await env.DB.prepare(
      "SELECT role FROM members WHERE workspace_id=? AND user_id=?",
    )
      .bind(id, user.id)
      .first();
    if (member?.role !== root.role)
      await env.DB.prepare(
        "INSERT INTO members(workspace_id,user_id,role) VALUES(?,?,?) ON CONFLICT(workspace_id,user_id) DO UPDATE SET role=excluded.role",
      )
        .bind(id, user.id, root.role)
        .run();
    const headers = new Headers(request.headers);
    headers.set("X-Zwart-Product", stored.product);
    return legacy(new Request(request, { headers }), env);
  }
  if (!canonical) return legacy(request, env);
  const areaMatch = route.match(/^areas\/([^/]+)$/);
  const ownRoute =
    route === "areas" ||
    areaMatch ||
    route === "hub" ||
    route === "hub/tasks" ||
    route === "hub/agenda" ||
    route === "hub/search" ||
    route === "focus" ||
    route === "focus/start" ||
    route === "focus/stop" ||
    route === "export" ||
    route === "audit" ||
    route === "trash" ||
    route.startsWith("restore/") ||
    route.match(/^projects\/[^/]+\/(hub|links)(?:\/[^/]+)?$/);
  if (!ownRoute) {
    if (route.startsWith("records/focus_sessions") && mutating) {
      if (
        method === "DELETE" &&
        /^records\/focus_sessions\/[^/]+$/.test(route)
      ) {
        const user = await authorize(request, env, true);
        const root = await rootAccess(env, user, id, true);
        const record = await getRecord(
          env,
          id,
          route.split("/")[2],
          "focus_sessions",
        );
        if (record.status !== "done")
          fail(409, "Selesaikan sesi fokus sebelum menghapus riwayatnya.");
        if (record.data.user_id !== user.id && root.role !== "owner")
          fail(403, "Riwayat fokus ini milik pengguna lain.");
        return json(
          await deleteRecord(env, id, user, PRODUCTS["daily-apps"], record.id),
        );
      }
      fail(403, "Gunakan timer fokus untuk mencatat waktu aktual.");
    }
    if (method === "DELETE" && route.startsWith("records/projects/")) {
      const user = await authorize(request, env, true);
      await rootAccess(env, user, id, true);
      const project = route.split("/")[2];
      const linked = await env.DB.prepare(
        "SELECT record_id FROM workspace_project_links WHERE root_id=? AND project_id=? LIMIT 1",
      )
        .bind(id, project)
        .first();
      if (linked)
        fail(409, "Lepaskan tautan hasil kerja proyek sebelum menghapusnya.");
    }
    return legacy(request, env);
  }
  const user = await authorize(request, env, mutating);
  await rootAccess(env, user, id, mutating);
  if (route === "areas" && method === "GET")
    return json({ areas: await areas(env, id) });
  if (areaMatch && method === "POST")
    return json({ workspace: await ensureArea(env, user, id, areaMatch[1]) });
  if (route === "hub" && method === "GET")
    return json(await summary(env, id, user, url.searchParams.get("today")));
  if (route === "hub/tasks" && method === "GET") {
    const rows = await env.DB.prepare(
      "SELECT * FROM records WHERE workspace_id=? AND kind='tasks' AND deleted_at IS NULL ORDER BY created_at DESC LIMIT 1001",
    )
      .bind(id)
      .all();
    const truncated = rows.results.length > 1000;
    return json({
      records: rows.results
        .slice(0, 1000)
        .map((r) => ({ ...r, data: JSON.parse(r.data) })),
      truncated,
    });
  }
  if (route === "export" && method === "GET") {
    const rows = await env.DB.prepare(
      `SELECT r.*,w.product AS area FROM records r JOIN workspaces w ON w.id=r.workspace_id WHERE ${scope} AND r.deleted_at IS NULL ORDER BY w.product,r.kind,r.created_at`,
    )
      .bind(id, id)
      .all();
    const membership = await rootAccess(env, user, id);
    const links = await env.DB.prepare(
      "SELECT project_id,record_id,created_at FROM workspace_project_links WHERE root_id=?",
    )
      .bind(id)
      .all();
    return json({
      version: 3,
      workspace: { id, name: membership.name },
      exportedAt: new Date().toISOString(),
      areas: await areas(env, id),
      records: await Promise.all(
        rows.results.map((r) => present(env, r, membership.role)),
      ),
      project_links: links.results,
    });
  }
  if (route === "audit" && method === "GET") {
    const rows = await env.DB.prepare(
      "SELECT a.*,u.name AS actor,w.product AS area FROM audit a JOIN users u ON u.id=a.actor_id JOIN workspaces w ON w.id=a.workspace_id WHERE (a.workspace_id=? OR a.workspace_id IN (SELECT workspace_id FROM workspace_areas WHERE root_id=?)) ORDER BY a.created_at DESC LIMIT 100",
    )
      .bind(id, id)
      .all();
    return json({ entries: rows.results });
  }
  if (route === "trash" && method === "GET") {
    const rows = await env.DB.prepare(
      `SELECT r.id,r.kind,r.title,r.deleted_at,w.product AS area FROM records r JOIN workspaces w ON w.id=r.workspace_id WHERE ${scope} AND r.deleted_at IS NOT NULL ORDER BY r.deleted_at DESC LIMIT 100`,
    )
      .bind(id, id)
      .all();
    return json({ records: rows.results });
  }
  if (route.startsWith("restore/") && method === "POST") {
    const record = await env.DB.prepare(
      `SELECT r.workspace_id,w.product FROM records r JOIN workspaces w ON w.id=r.workspace_id WHERE ${scope} AND r.id=? AND r.deleted_at IS NOT NULL`,
    )
      .bind(id, id, route.split("/")[1])
      .first();
    if (!record) fail(404, "Data tidak ditemukan.");
    if (record.workspace_id === id) return legacy(request, env);
    const child = new URL(request.url);
    child.pathname = "/api/workspaces/" + record.workspace_id + "/" + route;
    const headers = new Headers(request.headers);
    return unifiedRouter(
      new Request(child, { method, headers, body: await request.text() }),
      env,
      legacy,
    );
  }
  if (route === "hub/agenda" && method === "GET")
    return json(
      await agenda(
        env,
        id,
        url.searchParams.get("month") || new Date().toISOString().slice(0, 7),
      ),
    );
  if (route === "hub/search" && method === "GET") {
    const q = (url.searchParams.get("q") || "").trim().slice(0, 100);
    if (q.length < 2) return json({ records: [] });
    const rows = await env.DB.prepare(
      `SELECT r.id,r.workspace_id,r.kind,r.title,r.status,r.updated_at,w.product AS area FROM records r JOIN workspaces w ON w.id=r.workspace_id WHERE ${scope} AND r.deleted_at IS NULL AND r.title LIKE ? ORDER BY r.updated_at DESC LIMIT 50`,
    )
      .bind(id, id, "%" + q + "%")
      .all();
    return json({ records: rows.results });
  }
  if (route === "focus" && method === "GET") {
    const row = await env.DB.prepare(
      "SELECT * FROM records WHERE workspace_id=? AND kind='focus_sessions' AND status='active' AND deleted_at IS NULL AND json_extract(data,'$.user_id')=?",
    )
      .bind(id, user.id)
      .first();
    return json({ focus: row ? { ...row, data: JSON.parse(row.data) } : null });
  }
  if (route === "focus/start" && method === "POST")
    return json(await startFocus(env, user, id, await body(request)), 201);
  if (route === "focus/stop" && method === "POST")
    return json(await stopFocus(env, user, id, await body(request)));
  const projectMatch = route.match(
    /^projects\/([^/]+)\/(hub|links)(?:\/([^/]+))?$/,
  );
  if (projectMatch) {
    const project = projectMatch[1];
    await getRecord(env, id, project, "projects");
    if (projectMatch[2] === "hub" && method === "GET")
      return json(await projectHub(env, id, project));
    if (projectMatch[2] === "links" && method === "POST") {
      const input = await body(request);
      const target = await env.DB.prepare(
        `SELECT r.id FROM records r WHERE ${scope} AND r.id=? AND r.deleted_at IS NULL`,
      )
        .bind(id, id, input.record_id)
        .first();
      if (!target)
        fail(404, "Hasil kerja tidak ditemukan dalam workspace ini.");
      if (target.id === project)
        fail(422, "Proyek tidak dapat ditautkan ke dirinya sendiri.");
      await env.DB.batch([
        env.DB.prepare(
          "INSERT OR IGNORE INTO workspace_project_links(root_id,project_id,record_id,actor_id,created_at) VALUES(?,?,?,?,?)",
        ).bind(id, project, target.id, user.id, Date.now()),
        auditStatement(env, id, user, "project.link", project, target.id),
      ]);
      return json({ ok: true });
    }
    if (projectMatch[2] === "links" && projectMatch[3] && method === "DELETE") {
      await env.DB.batch([
        env.DB.prepare(
          "DELETE FROM workspace_project_links WHERE root_id=? AND project_id=? AND record_id=?",
        ).bind(id, project, projectMatch[3]),
        auditStatement(
          env,
          id,
          user,
          "project.unlink",
          project,
          projectMatch[3],
        ),
      ]);
      return json({ ok: true });
    }
  }
  fail(405, "Metode tidak tersedia.");
}
