import React, { useState, useEffect, useCallback } from "react";
import { createRoot } from "react-dom/client";
import {
  Menu,
  X,
  Search,
  Sun,
  Moon,
  LogOut,
  Settings,
  ArrowUpRight,
  ArrowRight,
  Plus,
  Check,
  Play,
  Square,
  LayoutDashboard,
  FolderKanban,
  ListTodo,
  CalendarDays,
  Wrench,
  Database,
  BarChart3,
  Clock,
  ChevronLeft,
  Link2,
  Unlink,
  RefreshCw,
  Download,
} from "lucide-react";
import { PRODUCTS } from "../platform/definitions.js";
import {
  api,
  setCsrf,
  download,
  date,
  dateTime,
  localDate,
  labels,
} from "./api.js";
import {
  Auth,
  Recovery,
  Onboarding,
  Records,
  RecordForm,
  SettingsView,
  ToolBoundary,
  Brand,
  ErrorBox,
  Empty,
  Loading,
  Status,
  Modal,
} from "./legacy-ui.jsx";
const ToolPanel = React.lazy(() =>
  import("./tools.jsx").then((m) => ({ default: m.ToolPanel })),
);
import { PublicForm } from "./forms.jsx";
import { AREA_LABELS, GROUPS, TOOLS, FLOWS } from "./catalog.js";
import "./style.css";
import "./workspace.css";
const product = PRODUCTS["daily-apps"];
const PAGES = [
  ["today", "Hari ini", LayoutDashboard],
  ["projects", "Proyek", FolderKanban],
  ["tasks", "Papan tugas", ListTodo],
  ["agenda", "Agenda", CalendarDays],
  ["tools", "Alat kerja", Wrench],
  ["data", "Data & operasi", Database],
  ["reports", "Laporan", BarChart3],
];
const readRoute = () => {
  try {
    return location.hash
      .slice(1)
      .split("/")
      .filter(Boolean)
      .map(decodeURIComponent);
  } catch {
    return ["today"];
  }
};
function useData(path, revision = 0) {
  const [state, setState] = useState({ data: null, error: "" });
  useEffect(() => {
    let live = true;
    setState({ data: null, error: "" });
    api(path)
      .then((data) => live && setState({ data, error: "" }))
      .catch((e) => live && setState({ data: null, error: e.message }));
    return () => {
      live = false;
    };
  }, [path, revision]);
  return state;
}
function App() {
  const [auth, setAuth] = useState(null),
    [workspace, setWorkspace] = useState(null),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(""),
    [recovery, setRecovery] = useState(""),
    [route, setRoute] = useState(readRoute),
    [mobile, setMobile] = useState(false),
    [toast, setToast] = useState(""),
    [revision, setRevision] = useState(0),
    [query, setQuery] = useState("");
  const [theme, setTheme] = useState(
    () => localStorage.getItem("zwart04.theme") || "light",
  );
  const notice = useCallback((text) => {
      setToast(text);
    }, []),
    refresh = () => setRevision((v) => v + 1);
  const navigate = (...path) => {
    location.hash = path.map(encodeURIComponent).join("/");
    setMobile(false);
    window.scrollTo(0, 0);
  };
  useEffect(() => {
    const changed = () => setRoute(readRoute());
    window.addEventListener("hashchange", changed);
    return () => window.removeEventListener("hashchange", changed);
  }, []);
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(""), 5500);
    return () => clearTimeout(timer);
  }, [toast]);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.setProperty("--accent", "#b8d97a");
    document.title = "Daily Workspace · Dari rencana sampai selesai";
    localStorage.setItem("zwart04.theme", theme);
  }, [theme]);
  const signedIn = (data) => {
    setAuth(data);
    setWorkspace(
      data.workspaces?.find(
        (w) => w.id === localStorage.getItem("daily.workspace"),
      ) ||
        data.workspaces?.[0] ||
        null,
    );
    setRecovery(data.recoveryCode || "");
    setError("");
  };
  useEffect(() => {
    api("/auth/session")
      .then((d) => (d.user ? signedIn(d) : setAuth(null)))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
    const expired = () => {
      setAuth(null);
      setWorkspace(null);
      setCsrf("");
      notice("Session berakhir. Silakan masuk kembali.");
    };
    window.addEventListener("session-expired", expired);
    return () => window.removeEventListener("session-expired", expired);
  }, [notice]);
  useEffect(() => {
    if (workspace) localStorage.setItem("daily.workspace", workspace.id);
  }, [workspace?.id]);
  const invite = new URLSearchParams(location.search).get("invite");
  useEffect(() => {
    if (auth && invite)
      api("/invitations/accept", "POST", { token: invite })
        .then((d) => {
          setAuth((v) => ({ ...v, ...d }));
          setWorkspace(d.workspaces.at(-1));
          history.replaceState({}, "", location.pathname);
          notice("Undangan diterima.");
        })
        .catch((e) => notice(e.message));
  }, [auth?.user?.id, invite]);
  const logout = async () => {
    try {
      await api("/auth/logout", "POST", {});
      setAuth(null);
      setWorkspace(null);
      setCsrf("");
    } catch (e) {
      notice(e.message);
    }
  };
  const token = new URLSearchParams(location.search).get("form");
  if (token) return <PublicForm token={token} />;
  if (loading)
    return (
      <div className="center-screen">
        <Brand />
        <Loading />
      </div>
    );
  if (!auth)
    return (
      <Auth
        signedIn={signedIn}
        initialError={error}
        theme={theme}
        toggleTheme={() => setTheme((v) => (v === "light" ? "dark" : "light"))}
      />
    );
  if (recovery)
    return <Recovery code={recovery} done={() => setRecovery("")} />;
  if (!workspace)
    return (
      <Onboarding
        user={auth.user}
        created={(ws) => {
          setWorkspace(ws);
          setAuth((v) => ({ ...v, workspaces: [...(v.workspaces || []), ws] }));
        }}
      />
    );
  const page = route[0] || "today",
    context = {
      product,
      workspace,
      user: auth.user,
      notice,
      refresh,
      revision,
      navigate,
      openRecord: (r) =>
        navigate("record", r.area || "daily-apps", r.kind, r.id),
    };
  const heading =
    PAGES.find((p) => p[0] === page)?.[1] ||
    {
      project: "Detail proyek",
      record: "Catatan",
      tool: "Alat kerja",
      settings: "Pengaturan",
      search: "Pencarian",
    }[page] ||
    "Workspace";
  const view =
    page === "today" ? (
      <Today {...context} />
    ) : page === "projects" ? (
      <Projects {...context} />
    ) : page === "project" ? (
      <Project {...context} id={route[1]} />
    ) : page === "tasks" ? (
      <TaskBoard {...context} />
    ) : page === "agenda" ? (
      <Agenda {...context} />
    ) : page === "tools" ? (
      <Library {...context} tools />
    ) : page === "data" ? (
      <Library {...context} />
    ) : page === "reports" ? (
      <WorkspaceReports {...context} />
    ) : page === "record" || page === "tool" ? (
      <AreaPane
        {...context}
        area={route[1]}
        moduleKey={route[2]}
        initialRecordId={route[3]}
      />
    ) : page === "settings" ? (
      <SettingsView
        {...context}
        auth={auth}
        updateAuth={setAuth}
        updateWorkspace={setWorkspace}
      />
    ) : page === "search" ? (
      <SearchResults {...context} query={route[1] || ""} />
    ) : (
      <Empty title="Halaman tidak ditemukan" />
    );
  return (
    <div className="workspace-shell">
      <a
        className="skip-link"
        href="#main-content"
        onClick={(e) => {
          e.preventDefault();
          document.getElementById("main-content").focus();
        }}
      >
        Ke isi halaman
      </a>
      {mobile && (
        <button
          className="mobile-scrim"
          aria-label="Tutup menu"
          onClick={() => setMobile(false)}
        />
      )}
      <aside
        className={"sidebar " + (mobile ? "open" : "")}
        aria-label="Menu utama"
      >
        <div className="sidebar-brand">
          <Brand />
          <button
            className="icon-button mobile-only"
            aria-label="Tutup menu"
            onClick={() => setMobile(false)}
          >
            <X size={20} />
          </button>
        </div>
        <div className="workspace-picker">
          <span className="workspace-icon">{workspace.name.slice(0, 1)}</span>
          <div>
            <small>RUANG KERJA</small>
            <select
              aria-label="Ruang kerja aktif"
              value={workspace.id}
              onChange={(e) => {
                setWorkspace(
                  auth.workspaces.find((w) => w.id === e.target.value),
                );
                navigate("today");
              }}
            >
              {auth.workspaces.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <nav>
          {PAGES.map(([key, label, Icon]) => (
            <button
              key={key}
              aria-current={page === key ? "page" : undefined}
              className={page === key ? "selected" : ""}
              onClick={() => navigate(key)}
            >
              <Icon size={18} />
              {label}
              {key === "today" && <span className="nav-dot" />}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <button
            className={page === "settings" ? "selected" : ""}
            onClick={() => navigate("settings")}
          >
            <Settings size={18} />
            Pengaturan & anggota
          </button>
          <button
            onClick={() => setTheme((v) => (v === "light" ? "dark" : "light"))}
          >
            {theme === "light" ? <Moon size={18} /> : <Sun size={18} />}Mode{" "}
            {theme === "light" ? "gelap" : "terang"}
          </button>
          <div className="sidebar-person">
            <span className="avatar">
              {auth.user.name.slice(0, 2).toUpperCase()}
            </span>
            <div>
              <strong>{auth.user.name}</strong>
              <small>{workspace.role}</small>
            </div>
            <button
              className="icon-button"
              aria-label="Keluar"
              onClick={logout}
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div>
            <button
              className="icon-button mobile-only"
              aria-expanded={mobile}
              aria-label="Buka menu"
              onClick={() => setMobile(true)}
            >
              <Menu size={22} />
            </button>
            <span className="breadcrumb">
              Workspace<span>/</span>
              <strong>{heading}</strong>
            </span>
          </div>
          <form
            className="global-search"
            onSubmit={(e) => {
              e.preventDefault();
              if (query.trim().length >= 2) navigate("search", query.trim());
            }}
          >
            <Search size={17} />
            <input
              aria-label="Cari di seluruh workspace"
              placeholder="Cari pekerjaan…"
              minLength={2}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button aria-label="Cari">
              <ArrowRight size={16} />
            </button>
          </form>
        </header>
        <main id="main-content" tabIndex={-1} className="main-content">
          <ToolBoundary key={workspace.id + route.join("/")}>
            <FocusStrip {...context} />
            {view}
          </ToolBoundary>
        </main>
      </div>
      {toast && (
        <div className="toast" role="status">
          <Check size={18} />
          {toast}
        </div>
      )}
    </div>
  );
}
function Heading({ eyebrow, title, description, children }) {
  return (
    <div className="page-heading">
      <div>
        <p className="eyebrow">{eyebrow || "DAILY WORKSPACE"}</p>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {children}
    </div>
  );
}
function State({ data, error, children }) {
  return error ? <ErrorBox message={error} /> : !data ? <Loading /> : children;
}
function Row({ record, openRecord, extra }) {
  return (
    <div className="work-row">
      <button onClick={() => openRecord(record)}>
        <strong>{record.title}</strong>
        <small>
          {AREA_LABELS[record.area || "daily-apps"]} ·{" "}
          {
            PRODUCTS[record.area || "daily-apps"]?.modules.find(
              (m) => m.key === record.kind,
            )?.label
          }
        </small>
      </button>
      {extra || <Status value={record.status} />}
      <button
        className="icon-button"
        aria-label={"Buka " + record.title}
        onClick={() => openRecord(record)}
      >
        <ArrowUpRight size={17} />
      </button>
    </div>
  );
}
function Today(c) {
  const { workspace, revision, user, navigate, openRecord } = c,
    { data, error } = useData(
      `/workspaces/${workspace.id}/hub?today=${localDate()}`,
      revision,
    );
  return (
    <>
      <Heading
        eyebrow={date(new Date()).toUpperCase()}
        title={"Selamat bekerja, " + user.name.split(" ")[0] + "."}
        description="Satu tempat untuk merencanakan, membuat, dan menyelesaikan pekerjaan."
      >
        <button className="primary" onClick={() => navigate("projects")}>
          <Plus size={17} />
          Mulai proyek
        </button>
      </Heading>
      <State data={data} error={error}>
        {data && (
          <>
            <section className="daily-hero">
              <div>
                <span className="pill">RUANG UNTUK PROGRES</span>
                <h2>
                  Dari rencana
                  <br />
                  sampai selesai<span>.</span>
                </h2>
                <p>
                  {data.total
                    ? `${data.total} catatan pekerjaan Anda, terhubung dalam satu ruang.`
                    : "Mulai dengan tujuan Anda. Susun tugas, kerjakan, lalu tautkan hasilnya ke proyek."}
                </p>
                <button className="hero-link" onClick={() => navigate("tasks")}>
                  Buka papan tugas <ArrowRight size={18} />
                </button>
              </div>
              <div className="hero-graphic" aria-hidden="true">
                <div className="orbit-ring" />
                <div className="orbit-ring inner" />
                <span className="orbit-core">
                  <Check size={38} />
                </span>
                <span className="orbit-tag plan">Rencanakan</span>
                <span className="orbit-tag create">Kerjakan</span>
                <span className="orbit-tag done">Selesaikan</span>
              </div>
            </section>
            <div className="overview-metrics">
              <Metric
                label="Proyek aktif"
                value={
                  data.projects.filter((p) => p.status === "active").length
                }
              />
              <Metric label="Tugas jatuh tempo" value={data.due.length} />
              <Metric label="Catatan tersimpan" value={data.total} />
              <Metric label="Catatan selesai" value={data.done} />
            </div>
            <div className="dashboard-grid">
              <section className="panel">
                <div className="panel-heading">
                  <div>
                    <h2>Prioritas hari ini</h2>
                    <p>Tugas hari ini dan yang melewati tenggat.</p>
                  </div>
                  <button
                    className="text-button"
                    onClick={() => navigate("tasks")}
                  >
                    Lihat semua
                  </button>
                </div>
                {data.due.length ? (
                  <div className="work-list">
                    {data.due.map((r) => (
                      <Row
                        key={r.id}
                        record={r}
                        openRecord={openRecord}
                        extra={
                          <span className="pill">{date(r.data.date)}</span>
                        }
                      />
                    ))}
                  </div>
                ) : (
                  <Empty
                    title="Tidak ada tugas jatuh tempo"
                    description="Susun tugas dan tentukan tanggalnya di papan tugas."
                    action={
                      <button
                        className="secondary"
                        onClick={() => navigate("tasks")}
                      >
                        Susun tugas
                      </button>
                    }
                  />
                )}
              </section>
              <section className="panel">
                <div className="panel-heading">
                  <h2>Alur kerja Anda</h2>
                </div>
                <div className="journey-list">
                  {[
                    [
                      "01",
                      "Rencanakan",
                      "Tentukan proyek dan hasil yang ingin dicapai.",
                      "projects",
                    ],
                    [
                      "02",
                      "Kerjakan",
                      "Pilih tugas, gunakan alat kerja, dan catat waktu.",
                      "tools",
                    ],
                    [
                      "03",
                      "Hubungkan hasil",
                      "Tautkan catatan atau hasil kerja ke proyek.",
                      "projects",
                    ],
                  ].map(([n, title, desc, to]) => (
                    <button key={n} onClick={() => navigate(to)}>
                      <span>{n}</span>
                      <div>
                        <strong>{title}</strong>
                        <p>{desc}</p>
                      </div>
                      <ArrowUpRight size={17} />
                    </button>
                  ))}
                </div>
              </section>
            </div>
            <section className="panel">
              <div className="panel-heading">
                <h2>Terakhir dikerjakan</h2>
                <Clock size={18} />
              </div>
              {data.recent.length ? (
                <div className="work-list">
                  {data.recent.map((r) => (
                    <Row key={r.id} record={r} openRecord={openRecord} />
                  ))}
                </div>
              ) : (
                <Empty
                  title="Belum ada pekerjaan"
                  description="Semua angka dan aktivitas di sini berasal dari data Anda sendiri."
                />
              )}
            </section>
            {data.truncated && (
              <p className="muted">
                Ringkasan detail menampilkan 5.000 catatan terbaru; jumlah total
                mencakup seluruh data.
              </p>
            )}
          </>
        )}
      </State>
    </>
  );
}
function Metric({ label, value }) {
  return (
    <div>
      <small>{label}</small>
      <strong>{value}</strong>
    </div>
  );
}
function Projects(c) {
  const { workspace, revision, navigate } = c,
    { data, error } = useData(
      `/workspaces/${workspace.id}/records/projects?page=1`,
      revision,
    ),
    [editing, setEditing] = useState(false),
    module = product.modules.find((m) => m.key === "projects");
  return (
    <>
      <Heading
        title="Bangun sesuatu yang berarti."
        description="Satukan tugas, waktu kerja, dan hasil dari seluruh bidang dalam sebuah proyek."
      >
        {workspace.role !== "viewer" && (
          <button className="primary" onClick={() => setEditing(true)}>
            <Plus size={17} />
            Proyek baru
          </button>
        )}
      </Heading>
      <State data={data} error={error}>
        {data?.records.length ? (
          <div className="project-grid">
            {data.records.map((r) => (
              <button
                className="panel project-card"
                key={r.id}
                onClick={() => navigate("project", r.id)}
              >
                <span className="project-symbol">
                  <FolderKanban size={24} />
                </span>
                <Status value={r.status} />
                <h2>{r.title}</h2>
                <p>
                  {r.data.description ||
                    "Buka proyek untuk menyusun tugas dan menghubungkan hasil kerja."}
                </p>
                <footer>
                  <span>
                    {r.data.deadline
                      ? "Tenggat " + date(r.data.deadline)
                      : "Tanpa tenggat"}
                  </span>
                  <ArrowUpRight size={18} />
                </footer>
              </button>
            ))}
          </div>
        ) : (
          <Empty
            title="Proyek pertama dimulai dari sini"
            description="Tentukan tujuan nyata, uraikan menjadi tugas, dan kumpulkan hasil pekerjaan Anda."
            action={
              workspace.role !== "viewer" && (
                <button className="primary" onClick={() => setEditing(true)}>
                  Buat proyek
                </button>
              )
            }
          />
        )}
        {data?.pages > 1 && (
          <button
            className="secondary"
            onClick={() => navigate("record", "daily-apps", "projects")}
          >
            Lihat seluruh {data.total} proyek
          </button>
        )}
      </State>
      {editing && (
        <RecordForm
          {...c}
          module={module}
          record={{}}
          close={() => setEditing(false)}
          saved={() => {
            setEditing(false);
            c.refresh();
            c.notice("Proyek dibuat.");
          }}
        />
      )}
    </>
  );
}
function Project(c) {
  const { workspace, id, revision, refresh, notice, navigate, openRecord } = c,
    { data, error } = useData(
      `/workspaces/${workspace.id}/projects/${id}/hub`,
      revision,
    ),
    [edit, setEdit] = useState(false),
    [addTask, setAddTask] = useState(false),
    [linking, setLinking] = useState(false);
  return (
    <>
      <button
        className="text-button back-link"
        onClick={() => navigate("projects")}
      >
        <ChevronLeft size={16} />
        Semua proyek
      </button>
      <State data={data} error={error}>
        {data && (
          <>
            <Heading
              eyebrow="PROYEK TERHUBUNG"
              title={data.project.title}
              description={data.project.data.description}
            >
              {workspace.role !== "viewer" && (
                <button className="secondary" onClick={() => setEdit(true)}>
                  Edit proyek
                </button>
              )}
            </Heading>
            <div className="overview-metrics">
              <Metric
                label="Tugas selesai"
                value={`${data.progress.done}/${data.progress.total}`}
              />
              <Metric
                label="Waktu fokus"
                value={duration(data.focus_seconds)}
              />
              <Metric label="Hasil terhubung" value={data.links.length} />
              <Metric
                label="Tenggat"
                value={date(data.project.data.deadline)}
              />
            </div>
            <div className="project-progress">
              <div
                style={{
                  width:
                    (data.progress.total
                      ? (100 * data.progress.done) / data.progress.total
                      : 0) + "%",
                }}
              />
            </div>
            <div className="dashboard-grid">
              <section className="panel">
                <div className="panel-heading">
                  <h2>Rencana & pelaksanaan</h2>
                  {workspace.role !== "viewer" && (
                    <button
                      className="secondary small"
                      onClick={() => setAddTask(true)}
                    >
                      <Plus size={15} />
                      Tugas
                    </button>
                  )}
                </div>
                <TaskColumns {...c} rows={data.tasks} />
              </section>
              <section className="panel">
                <div className="panel-heading">
                  <h2>Hasil pekerjaan</h2>
                  {workspace.role !== "viewer" && (
                    <button
                      className="secondary small"
                      onClick={() => setLinking(true)}
                    >
                      <Link2 size={15} />
                      Tautkan
                    </button>
                  )}
                </div>
                {data.links.length ? (
                  <div className="work-list">
                    {data.links.map((r) => (
                      <Row
                        key={r.id}
                        record={r}
                        openRecord={openRecord}
                        extra={
                          workspace.role !== "viewer" ? (
                            <button
                              className="icon-button"
                              aria-label={"Lepaskan " + r.title}
                              onClick={() =>
                                api(
                                  `/workspaces/${workspace.id}/projects/${id}/links/${r.id}`,
                                  "DELETE",
                                )
                                  .then(refresh)
                                  .catch((e) => notice(e.message))
                              }
                            >
                              <Unlink size={17} />
                            </button>
                          ) : null
                        }
                      />
                    ))}
                  </div>
                ) : (
                  <Empty
                    title="Hubungkan pekerjaan Anda"
                    description="Tautkan pesanan, dokumen, materi belajar, atau hasil studio yang sudah Anda simpan."
                    action={
                      <button
                        className="secondary"
                        onClick={() => navigate("tools")}
                      >
                        Buka alat kerja
                      </button>
                    }
                  />
                )}
              </section>
            </div>
            {edit && (
              <RecordForm
                {...c}
                module={product.modules.find((m) => m.key === "projects")}
                record={data.project}
                close={() => setEdit(false)}
                saved={() => {
                  setEdit(false);
                  refresh();
                }}
              />
            )}
            {addTask && (
              <RecordForm
                {...c}
                module={product.modules.find((m) => m.key === "tasks")}
                record={{ data: { project_id: id } }}
                close={() => setAddTask(false)}
                saved={() => {
                  setAddTask(false);
                  refresh();
                }}
              />
            )}
            {linking && <LinkResults {...c} close={() => setLinking(false)} />}
          </>
        )}
      </State>
    </>
  );
}
function LinkResults({ workspace, id, close, refresh, notice }) {
  const [q, setQ] = useState(""),
    [search, setSearch] = useState("");
  useEffect(() => {
    const timer = setTimeout(() => setSearch(q), 250);
    return () => clearTimeout(timer);
  }, [q]);
  const { data, error } = useData(
    `/workspaces/${workspace.id}/hub/search?q=${encodeURIComponent(search)}`,
  );
  return (
    <Modal title="Tautkan hasil pekerjaan" close={close}>
      <div className="modal-body">
        <label>
          Cari nama catatan
          <input
            autoFocus
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Minimal 2 karakter"
          />
        </label>
        {error && <ErrorBox message={error} />}
        <div className="work-list">
          {data?.records
            .filter((r) => r.id !== id)
            .map((r) => (
              <div className="work-row" key={r.id}>
                <span>
                  <strong>{r.title}</strong>
                  <small>{AREA_LABELS[r.area]}</small>
                </span>
                <button
                  className="secondary small"
                  onClick={() =>
                    api(
                      `/workspaces/${workspace.id}/projects/${id}/links`,
                      "POST",
                      { record_id: r.id },
                    )
                      .then(() => {
                        refresh();
                        notice("Hasil ditautkan ke proyek.");
                        close();
                      })
                      .catch((e) => notice(e.message))
                  }
                >
                  Tautkan
                </button>
              </div>
            ))}
        </div>
        {search.length >= 2 && !data?.records.length && (
          <p>
            Belum ada catatan dengan nama itu. Simpan pekerjaan dahulu dari menu
            Data & operasi atau Alat kerja.
          </p>
        )}
      </div>
    </Modal>
  );
}
function TaskBoard(c) {
  const { workspace, revision } = c,
    { data, error } = useData(
      `/workspaces/${workspace.id}/hub/tasks`,
      revision,
    ),
    [edit, setEdit] = useState(false);
  return (
    <>
      <Heading
        title="Satu langkah lebih dekat."
        description="Ubah rencana menjadi pekerjaan yang selesai. Mulai fokus untuk mencatat waktu nyata."
      >
        {workspace.role !== "viewer" && (
          <button className="primary" onClick={() => setEdit(true)}>
            <Plus size={17} />
            Tambah tugas
          </button>
        )}
      </Heading>
      <State data={data} error={error}>
        {data && (
          <>
            <TaskColumns {...c} rows={data.records} />
            {data.truncated && (
              <button
                className="secondary"
                onClick={() => c.navigate("record", "daily-apps", "tasks")}
              >
                Lihat tugas lainnya
              </button>
            )}
          </>
        )}
      </State>
      {edit && (
        <RecordForm
          {...c}
          module={product.modules.find((m) => m.key === "tasks")}
          record={{}}
          close={() => setEdit(false)}
          saved={() => {
            setEdit(false);
            c.refresh();
          }}
        />
      )}
    </>
  );
}
function TaskColumns(c) {
  const { rows, workspace, refresh, notice, openRecord } = c;
  const move = async (r, status) => {
    try {
      await api(`/workspaces/${workspace.id}/records/tasks/${r.id}`, "PUT", {
        ...r.data,
        status,
        version: r.version,
      });
      refresh();
      notice("Status tugas diperbarui.");
    } catch (e) {
      notice(e.message);
    }
  };
  const start = async (r) => {
    try {
      await api(`/workspaces/${workspace.id}/focus/start`, "POST", {
        task_id: r.id,
      });
      refresh();
      notice("Sesi fokus dimulai. Waktu dihitung server.");
    } catch (e) {
      notice(e.message);
    }
  };
  return (
    <div className="kanban">
      {["todo", "doing", "done"].map((status) => (
        <section className="kanban-column" key={status}>
          <header>
            <span className={"column-dot " + status} />
            <h3>{labels[status]}</h3>
            <span>{rows.filter((r) => r.status === status).length}</span>
          </header>
          {rows
            .filter((r) => r.status === status)
            .map((r) => (
              <article className="task-card" key={r.id}>
                <button
                  className="task-title"
                  onClick={() => openRecord({ ...r, area: "daily-apps" })}
                >
                  {r.title}
                </button>
                <p>{r.data.notes}</p>
                <div className="task-meta">
                  <span className="pill">{r.data.priority || "normal"}</span>
                  <span>{date(r.data.date)}</span>
                </div>
                {workspace.role !== "viewer" && (
                  <footer>
                    <select
                      aria-label={"Status " + r.title}
                      value={r.status}
                      onChange={(e) => move(r, e.target.value)}
                    >
                      {["todo", "doing", "done"].map((s) => (
                        <option key={s} value={s}>
                          {labels[s]}
                        </option>
                      ))}
                    </select>
                    {status !== "done" && (
                      <button
                        className="icon-button"
                        aria-label={"Fokus " + r.title}
                        onClick={() => start(r)}
                      >
                        <Play size={16} />
                      </button>
                    )}
                  </footer>
                )}
              </article>
            ))}
          {!rows.some((r) => r.status === status) && (
            <div className="kanban-empty">Belum ada tugas</div>
          )}
        </section>
      ))}
    </div>
  );
}
const duration = (seconds) => {
  const s = Math.max(0, Math.floor(seconds));
  return `${Math.floor(s / 3600)
    .toString()
    .padStart(
      2,
      "0",
    )}:${Math.floor(s / 60) % 60 < 10 ? "0" : ""}${Math.floor(s / 60) % 60}:${(s % 60).toString().padStart(2, "0")}`;
};
function FocusStrip({ workspace, revision, refresh, notice }) {
  const { data } = useData(`/workspaces/${workspace.id}/focus`, revision),
    [now, setNow] = useState(Date.now()),
    [busy, setBusy] = useState(false);
  useEffect(() => {
    if (!data?.focus) return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [data?.focus?.id]);
  if (!data?.focus) return null;
  const stop = async (complete_task) => {
    setBusy(true);
    try {
      await api(`/workspaces/${workspace.id}/focus/stop`, "POST", {
        id: data.focus.id,
        complete_task,
      });
      refresh();
      notice("Waktu fokus disimpan.");
    } catch (e) {
      notice(e.message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <section className="focus-strip" aria-label="Sesi fokus aktif">
      <span className="live-dot" />
      <div>
        <small>SEDANG FOKUS</small>
        <strong>{data.focus.title}</strong>
      </div>
      <time>
        {duration((now - Date.parse(data.focus.data.started_at)) / 1000)}
      </time>
      <button
        className="secondary small"
        disabled={busy}
        onClick={() => stop(false)}
      >
        <Square size={14} />
        Selesai fokus
      </button>
      {data.focus.data.task_id && (
        <button
          className="primary small"
          disabled={busy}
          onClick={() => stop(true)}
        >
          <Check size={15} />
          Selesaikan tugas
        </button>
      )}
    </section>
  );
}
function Agenda(c) {
  const [month, setMonth] = useState(localDate().slice(0, 7)),
    { data, error } = useData(
      `/workspaces/${c.workspace.id}/hub/agenda?month=${month}`,
      c.revision,
    );
  const grouped = Object.groupBy(data?.events || [], (e) =>
    e.date.slice(0, 10),
  );
  return (
    <>
      <Heading
        title="Semua agenda, satu pandangan."
        description="Tenggat proyek, jadwal layanan, kegiatan, dan tanggal pekerjaan dari data Anda."
      />
      <label className="month-picker">
        Bulan
        <input
          type="month"
          required
          value={month}
          onChange={(e) => e.target.value && setMonth(e.target.value)}
        />
      </label>
      <State data={data} error={error}>
        {data && !data.events.length ? (
          <Empty
            title="Bulan ini belum ada agenda"
            description="Tanggal dari tugas dan catatan Anda akan muncul otomatis di sini."
          />
        ) : (
          Object.entries(grouped).map(([day, events]) => (
            <section className="panel agenda-day" key={day}>
              <h2>{date(day + "T12:00:00")}</h2>
              <div className="work-list">
                {events.map((r, i) => (
                  <Row
                    key={r.id + r.label + i}
                    record={r}
                    openRecord={c.openRecord}
                    extra={<span className="pill">{r.label}</span>}
                  />
                ))}
              </div>
            </section>
          ))
        )}
        {data?.truncated && (
          <p>
            Agenda dibatasi 1.000 catatan per bulan. Gunakan pencarian untuk
            catatan lain.
          </p>
        )}
      </State>
    </>
  );
}
function Library({ navigate, tools = false }) {
  const [q, setQ] = useState("");
  return (
    <>
      <Heading
        title={tools ? "Ruang untuk membuat." : "Jalankan pekerjaan Anda."}
        description={
          tools
            ? "Alat yang bekerja dengan berkas dan data Anda. Hasilnya dapat dihubungkan ke proyek."
            : "Satu ruang data untuk kegiatan pribadi, kreatif, dan operasional."
        }
      />
      <label className="library-search">
        <Search size={19} />
        <input
          aria-label={tools ? "Cari alat" : "Cari jenis data"}
          placeholder={
            tools ? "Cari alat kerja…" : "Cari jenis catatan atau kegiatan…"
          }
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </label>
      {tools ? (
        <div className="tool-library">
          {TOOLS.filter((t) =>
            (t.title + " " + t.description)
              .toLowerCase()
              .includes(q.toLowerCase()),
          ).map((t, i) => (
            <button
              className="panel tool-tile"
              key={t.area + t.key}
              onClick={() => navigate("tool", t.area, t.key)}
            >
              <span className="tool-number">
                {String(i + 1).padStart(2, "0")}
              </span>
              <ArrowUpRight size={19} />
              <h2>{t.title}</h2>
              <p>{t.description}</p>
            </button>
          ))}
        </div>
      ) : (
        GROUPS.map((group) => (
          <section className="library-group" key={group.name}>
            <h2>{group.name}</h2>
            <p>{group.description}</p>
            {group.areas.map((area) => {
              const modules = PRODUCTS[area].modules.filter(
                (m) =>
                  !m.tool &&
                  (m.label + " " + AREA_LABELS[area])
                    .toLowerCase()
                    .includes(q.toLowerCase()),
              );
              return modules.length ? (
                <details
                  className="panel resource-section"
                  key={area}
                  open={q ? true : undefined}
                >
                  <summary>
                    {AREA_LABELS[area]}
                    <span>{modules.length} jenis catatan</span>
                  </summary>
                  {FLOWS[area] && (
                    <div className="flow-steps">
                      {FLOWS[area].map(([key, label]) => (
                        <button
                          key={key}
                          onClick={() => navigate("record", area, key)}
                        >
                          {label}
                          <ArrowRight size={14} />
                        </button>
                      ))}
                    </div>
                  )}
                  <div className="resource-links">
                    {modules.map((m) => (
                      <button
                        key={m.key}
                        onClick={() => navigate("record", area, m.key)}
                      >
                        {m.label}
                        <ArrowUpRight size={14} />
                      </button>
                    ))}
                  </div>
                </details>
              ) : null;
            })}
          </section>
        ))
      )}
    </>
  );
}
function AreaPane(c) {
  const { area, moduleKey, workspace, revision, notice } = c,
    { data, error } = useData(`/workspaces/${workspace.id}/areas`, revision),
    [enabled, setEnabled] = useState(null),
    [failure, setFailure] = useState(""),
    [busy, setBusy] = useState(false);
  const spec = PRODUCTS[area],
    module = spec?.modules.find((m) => m.key === moduleKey);
  if (!module) return <Empty title="Jenis pekerjaan tidak ditemukan" />;
  const id = data?.areas[area] || enabled;
  const enable = async () => {
    setBusy(true);
    try {
      const d = await api(
        `/workspaces/${workspace.id}/areas/${area}`,
        "POST",
        {},
      );
      setEnabled(d.workspace.id);
    } catch (e) {
      setFailure(e.message);
    } finally {
      setBusy(false);
    }
  };
  if (!data || error) return <State data={data} error={error} />;
  if (!id)
    return (
      <>
        <Heading
          title={module.label}
          description="Bidang ini belum diaktifkan di ruang kerja ini."
        />
        {failure && <ErrorBox message={failure} />}
        <Empty
          title="Mulai bidang kerja ini"
          description="Tidak ada data contoh yang akan ditambahkan. Semua anggota ruang memiliki akses sesuai perannya."
          action={
            workspace.role !== "viewer" && (
              <button className="primary" disabled={busy} onClick={enable}>
                Aktifkan {AREA_LABELS[area]}
              </button>
            )
          }
        />
      </>
    );
  const props = {
    ...c,
    workspace: { ...workspace, id },
    product: { ...spec, name: AREA_LABELS[area] },
    module,
    navigate: (key) => c.navigate("record", area, key),
  };
  return (
    <>
      <div className="area-context">
        <button
          className="text-button"
          onClick={() => c.navigate(module.tool ? "tools" : "data")}
        >
          <ChevronLeft size={15} />
          {module.tool ? "Semua alat" : "Semua data"}
        </button>
        <span>
          {workspace.name} / {AREA_LABELS[area]}
        </span>
      </div>
      {module.tool ? (
        <React.Suspense fallback={<Loading />}>
          <ToolPanel {...props} />
        </React.Suspense>
      ) : (
        <Records {...props} />
      )}
    </>
  );
}
function SearchResults(c) {
  const { data, error } = useData(
    `/workspaces/${c.workspace.id}/hub/search?q=${encodeURIComponent(c.query)}`,
    c.revision,
  );
  return (
    <>
      <Heading
        title={"Hasil untuk “" + c.query + "”"}
        description="Pencarian nama catatan dari seluruh bidang dalam ruang kerja ini. Maksimum 50 hasil terbaru."
      />
      <State data={data} error={error}>
        {data?.records.length ? (
          <section className="panel work-list">
            {data.records.map((r) => (
              <Row key={r.id} record={r} openRecord={c.openRecord} />
            ))}
          </section>
        ) : (
          <Empty
            title="Belum ditemukan"
            description="Coba nama catatan yang lebih singkat atau periksa ruang kerja aktif Anda."
          />
        )}
      </State>
    </>
  );
}
function WorkspaceReports(c) {
  const { data, error } = useData(
    `/workspaces/${c.workspace.id}/hub`,
    c.revision,
  );
  return (
    <>
      <Heading
        title="Lihat progres yang sebenarnya."
        description="Ringkasan lintas bidang dan laporan rinci berdasarkan catatan tersimpan."
      >
        <button
          className="secondary"
          onClick={() =>
            api(`/workspaces/${c.workspace.id}/export`)
              .then((d) =>
                download(
                  "daily-workspace.json",
                  JSON.stringify(d, null, 2),
                  "application/json",
                ),
              )
              .catch((e) => c.notice(e.message))
          }
        >
          <Download size={17} />
          Ekspor semua data
        </button>
      </Heading>
      <State data={data} error={error}>
        {data && (
          <>
            <div className="overview-metrics">
              <Metric label="Catatan" value={data.total} />
              <Metric label="Status selesai" value={data.done} />
              <Metric label="Proyek" value={data.projects.length} />
              <Metric
                label="Bidang berisi data"
                value={new Set(data.counts.map((r) => r.area)).size}
              />
            </div>
            <div className="report-areas">
              {Object.entries(AREA_LABELS).map(([area, label]) => {
                const count = data.counts
                  .filter((r) => r.area === area)
                  .reduce((n, r) => n + r.count, 0);
                return (
                  <button
                    className="panel report-area"
                    key={area}
                    onClick={() => c.navigate("tool", area, "reports")}
                  >
                    <BarChart3 size={20} />
                    <span>
                      <strong>{label}</strong>
                      <small>{count} catatan · buka laporan terperinci</small>
                    </span>
                    <ArrowUpRight size={18} />
                  </button>
                );
              })}
            </div>
          </>
        )}
      </State>
    </>
  );
}
createRoot(document.getElementById("root")).render(<App />);
