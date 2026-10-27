import { PublicForm } from "./forms.jsx";
import React, { useState, useEffect, useCallback, useRef } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowRight,
  ArrowUpRight,
  Plus,
  Search,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
  LayoutDashboard,
  Settings,
  LogOut,
  Layers,
  Check,
  CheckCircle2,
  Clock,
  AlertCircle,
  Download,
  MoreHorizontal,
  Trash2,
  Pencil,
  Eye,
  Shield,
  Loader2,
  Users,
  FolderOpen,
  CalendarDays,
  Sparkles,
  Sun,
  Moon,
  Package,
  Activity,
  FileText,
} from "lucide-react";
import { PRODUCTS } from "../platform/definitions.js";
import {
  api,
  setCsrf,
  download,
  money,
  date,
  dateTime,
  localDate,
  localTime,
  csv,
  labels,
  actionLabels,
} from "./api.js";
import "./style.css";
const product = PRODUCTS[__PRODUCT_ID__];
class ToolBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: false };
  }
  static getDerivedStateFromError() {
    return { error: true };
  }
  render() {
    return this.state.error ? (
      <section className="panel settings-card" role="alert">
        <h2>Tool gagal dibuka</h2>
        <p>
          Muat ulang tool untuk mencoba kembali. Data yang sudah disimpan tetap
          tersedia.
        </p>
        <button
          className="primary"
          onClick={() => this.setState({ error: false })}
        >
          Coba kembali
        </button>
      </section>
    ) : (
      this.props.children
    );
  }
}
function Brand() {
  return (
    <div className="brand">
      <span className="brand-mark">{product.name[0]}</span>
      <span>{product.name}</span>
    </div>
  );
}
function Auth({ signedIn, initialError, theme, toggleTheme }) {
  const [mode, setMode] = useState("login"),
    [error, setError] = useState(initialError || ""),
    [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    const f = Object.fromEntries(new FormData(e.currentTarget));
    try {
      signedIn(await api("/auth/" + mode, "POST", f));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };
  const title =
    mode === "login"
      ? "Selamat datang kembali."
      : mode === "register"
        ? "Mulai workspace Anda."
        : "Pulihkan akses Anda.";
  return (
    <div className="auth-shell">
      <section className="auth-story">
        <Brand />
        <div className="story-content">
          <p className="eyebrow">YOUR WORK. ONE CLEAR WORKSPACE.</p>
          <h1>{product.tagline}</h1>
          <p>{product.purpose}</p>
          <div className="story-art">
            <div className="art-grid" />
            <span className="art-orbit one" />
            <span className="art-orbit two" />
            <div className="art-card">
              <Layers size={26} />
              <strong>
                Satu alur.
                <br />
                Semua terhubung.
              </strong>
              <div className="art-lines">
                <i />
                <i />
                <i />
              </div>
            </div>
          </div>
        </div>
        <small>ZWART04 / BUILT WITH PURPOSE</small>
      </section>
      <section className="auth-form-section">
        <button
          className="icon-button auth-theme"
          aria-label="Ganti tema"
          onClick={toggleTheme}
        >
          {theme === "light" ? <Moon size={20} /> : <Sun size={20} />}
        </button>
        <div className="auth-card">
          <div className="auth-symbol">
            <ArrowUpRight size={26} />
          </div>
          <h2>{title}</h2>
          <p>
            {mode === "login"
              ? "Masuk untuk melanjutkan pekerjaan Anda."
              : mode === "register"
                ? "Buat akun dan simpan data di workspace pribadi Anda."
                : "Gunakan kode pemulihan yang Anda simpan saat registrasi."}
          </p>
          <form onSubmit={submit}>
            {mode === "register" && (
              <label>
                Nama
                <input
                  name="name"
                  autoComplete="name"
                  required
                  maxLength={80}
                />
              </label>
            )}
            <label>
              Email
              <input
                type="email"
                name="email"
                autoComplete="email"
                required
                maxLength={254}
              />
            </label>
            {mode === "recover" && (
              <label>
                Kode pemulihan
                <input
                  name="code"
                  required
                  spellCheck="false"
                  autoComplete="off"
                />
              </label>
            )}
            <label>
              {mode === "recover" ? "Password baru" : "Password"}
              <input
                type="password"
                name="password"
                required
                minLength={mode === "login" ? 1 : 12}
                maxLength={128}
                autoComplete={
                  mode === "login" ? "current-password" : "new-password"
                }
              />
              {mode !== "login" && <small>Minimum 12 karakter.</small>}
            </label>
            {mode === "login" && (
              <button
                type="button"
                className="text-button forgot"
                onClick={() => {
                  setMode("recover");
                  setError("");
                }}
              >
                Lupa password?
              </button>
            )}
            {error && <ErrorBox message={error} />}
            <button className="primary full" disabled={busy}>
              {busy ? (
                <Loader2 className="spin" size={18} />
              ) : (
                <>
                  {mode === "login"
                    ? "Masuk"
                    : mode === "register"
                      ? "Buat akun"
                      : "Pulihkan akun"}
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>
          <div className="auth-switch">
            {mode === "login" ? "Belum punya akun?" : "Sudah punya akun?"}{" "}
            <button
              className="text-button"
              onClick={() => {
                setMode(mode === "login" ? "register" : "login");
                setError("");
              }}
            >
              {mode === "login" ? "Daftar sekarang" : "Masuk"}
            </button>
          </div>
          <div className="auth-security">
            <Shield size={15} />
            <span>Satu akun untuk seluruh bidang kerja Anda.</span>
          </div>
        </div>
      </section>
    </div>
  );
}
function Recovery({ code, done }) {
  const [saved, setSaved] = useState(false);
  return (
    <div className="center-screen">
      <section className="onboarding-card">
        <Shield className="large-icon" />
        <h1>Simpan kode pemulihan.</h1>
        <p>
          Kode ini dapat memulihkan akses jika Anda lupa password. Simpan di
          tempat pribadi; jangan bagikan kepada siapa pun.
        </p>
        <code className="recovery-code">{code}</code>
        <button
          className="secondary full"
          onClick={() => {
            download("kode-pemulihan-" + product.id + ".txt", code);
          }}
        >
          <Download size={18} />
          Unduh kode
        </button>
        <label className="check-label">
          <input
            type="checkbox"
            checked={saved}
            onChange={(e) => setSaved(e.target.checked)}
          />
          Saya sudah menyimpan kode pemulihan.
        </label>
        <button className="primary full" disabled={!saved} onClick={done}>
          Lanjutkan
          <ArrowRight size={18} />
        </button>
      </section>
    </div>
  );
}
function Onboarding({ user, created }) {
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const data = await api("/workspaces", "POST", {
        name: new FormData(e.currentTarget).get("name"),
      });
      created(data.workspace);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <div className="center-screen">
      <section className="onboarding-card">
        <Brand />
        <p className="eyebrow">LANGKAH PERTAMA</p>
        <h1>
          Halo, {user.name.split(" ")[0]}.<br />
          Beri nama ruang kerja Anda.
        </h1>
        <p>
          Mulai dengan workspace kosong. Anda dapat menambah data dan mengundang
          anggota setelah ini.
        </p>
        <form onSubmit={submit}>
          <label>
            Nama workspace
            <input name="name" required maxLength={100} autoFocus />
          </label>
          {error && <ErrorBox message={error} />}
          <button className="primary full" disabled={busy}>
            Buat workspace
            <ArrowRight size={18} />
          </button>
        </form>
      </section>
    </div>
  );
}
export function ErrorBox({ message }) {
  return (
    <div className="error-box" role="alert">
      <AlertCircle size={18} />
      <span>{message}</span>
    </div>
  );
}
export function Empty({
  title = "Belum ada data",
  description = "Tambahkan data pertama untuk memulai.",
  action,
}) {
  return (
    <div className="empty">
      <span className="empty-icon">
        <FolderOpen size={28} />
      </span>
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  );
}
export function Modal({ title, children, close, wide = false }) {
  const ref = useRef(),
    closeRef = useRef(close);
  closeRef.current = close;
  useEffect(() => {
    const previous = document.activeElement,
      overflow = document.body.style.overflow;
    const listener = (e) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        closeRef.current();
      }
      if (e.key === "Tab") {
        const nodes = [
          ...ref.current.querySelectorAll(
            'button:not(:disabled),input:not(:disabled),select:not(:disabled),textarea:not(:disabled),a[href],[tabindex="0"]',
          ),
        ].filter((el) => el.getClientRects().length);
        const first = nodes[0],
          last = nodes.at(-1);
        if (!nodes.length) {
          e.preventDefault();
          ref.current.focus();
        } else if (
          e.shiftKey &&
          (document.activeElement === first ||
            document.activeElement === ref.current)
        ) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    document.addEventListener("keydown", listener);
    document.body.style.overflow = "hidden";
    ref.current?.focus();
    return () => {
      document.removeEventListener("keydown", listener);
      document.body.style.overflow = overflow;
      previous?.focus();
    };
  }, []);
  return (
    <div
      className="modal-overlay"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) close();
      }}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className={"modal " + (wide ? "wide" : "")}
        tabIndex={-1}
        ref={ref}
      >
        <header>
          <h2>{title}</h2>
          <button
            aria-label="Tutup dialog"
            className="icon-button"
            onClick={close}
          >
            <X size={20} />
          </button>
        </header>
        {children}
      </section>
    </div>
  );
}

export const Loading = () => (
  <div className="loading">
    <Loader2 className="spin" size={22} />
    <span>Memuat data workspace…</span>
  </div>
);
export const Status = ({ value }) => (
  <span className={"status status-" + value}>{labels[value] || value}</span>
);
function Records(context) {
  const { workspace, module, product, notice, refresh, revision } = context,
    [data, setData] = useState(null),
    [error, setError] = useState(""),
    [search, setSearch] = useState(""),
    [status, setStatus] = useState(""),
    [page, setPage] = useState(1),
    [edit, setEdit] = useState(null),
    [detail, setDetail] = useState(null),
    [deleting, setDeleting] = useState(null),
    [acting, setActing] = useState(null);
  useEffect(() => {
    if (context.initialRecordId)
      api(
        `/workspaces/${workspace.id}/records/${module.key}/${context.initialRecordId}`,
      )
        .then((d) => setDetail(d.record))
        .catch((e) => setError(e.message));
  }, [context.initialRecordId, module.key, workspace.id]);
  const editable = workspace.role !== "viewer",
    base = `/workspaces/${workspace.id}/records/${module.key}`;
  useEffect(() => {
    setData(null);
    setSearch("");
    setStatus("");
    setPage(1);
  }, [module.key, workspace.id]);
  useEffect(() => {
    let live = true;
    const timer = setTimeout(
      () =>
        api(
          base +
            `?page=${page}&q=${encodeURIComponent(search)}&status=${status}`,
        )
          .then((d) => {
            if (live) {
              setData(d);
              setError("");
            }
          })
          .catch((e) => {
            if (live) setError(e.message);
          }),
      search ? 250 : 0,
    );
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [base, page, search, status, revision]);
  const reload = () => {
    refresh();
    setDetail(null);
  };
  const remove = async () => {
    try {
      await api(base + "/" + deleting.id, "DELETE");
      setDeleting(null);
      reload();
      notice("Data dipindahkan ke sampah.");
    } catch (e) {
      notice(e.message);
    }
  };
  const exportCsv = async () => {
    try {
      const full = await api(`/workspaces/${workspace.id}/export`);
      download(
        module.key + ".csv",
        csv(
          full.records.filter(
            (r) => r.kind === module.key && r.workspace_id === workspace.id,
          ),
          [
            "name",
            "status",
            ...module.fields.filter((f) => f.key !== "name").map((f) => f.key),
          ],
        ),
        "text/csv",
      );
    } catch (e) {
      notice(e.message);
    }
  };
  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">{product.name.toUpperCase()}</p>
          <h1>{module.label}</h1>
          <p>
            Kelola data {module.label.toLowerCase()} yang tersimpan di workspace
            Anda.
          </p>
        </div>
        <div className="button-group">
          <button className="secondary" onClick={exportCsv}>
            <Download size={17} />
            Ekspor CSV
          </button>
          {editable &&
            !["attempts", "form_responses", "focus_sessions"].includes(
              module.key,
            ) && (
              <button className="primary" onClick={() => setEdit({})}>
                <Plus size={17} />
                Tambah data
              </button>
            )}
        </div>
      </div>
      <section className="panel records-panel">
        <div className="list-toolbar">
          <label className="search-field">
            <Search size={18} />
            <input
              aria-label="Cari data"
              placeholder="Cari data…"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </label>
          <select
            aria-label="Filter status"
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
          >
            <option value="">Semua status</option>
            {module.statuses.map((s) => (
              <option key={s} value={s}>
                {labels[s] || s}
              </option>
            ))}
          </select>
          <span className="list-count">{data?.total ?? "…"} catatan</span>
        </div>
        {error ? (
          <ErrorBox message={error} />
        ) : !data ? (
          <Loading />
        ) : data.records.length ? (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Nama</th>
                    {module.fields
                      .filter(
                        (f) =>
                          f.key !== "name" &&
                          ![
                            "textarea",
                            "code",
                            "json",
                            "items",
                            "quiz",
                          ].includes(f.type),
                      )
                      .slice(0, 3)
                      .map((f) => (
                        <th key={f.key}>{f.label}</th>
                      ))}
                    <th>Status</th>
                    <th>Diperbarui</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {data.records.map((r) => (
                    <tr key={r.id}>
                      <td>
                        <button
                          className="record-name"
                          onClick={() => setDetail(r)}
                        >
                          {r.title}
                        </button>
                      </td>
                      {module.fields
                        .filter(
                          (f) =>
                            f.key !== "name" &&
                            ![
                              "textarea",
                              "code",
                              "json",
                              "items",
                              "quiz",
                            ].includes(f.type),
                        )
                        .slice(0, 3)
                        .map((f) => (
                          <td key={f.key}>
                            {displayValue(
                              f,
                              r.data[f.key],
                              product.currency,
                              false,
                              r.referenceNames,
                            )}
                          </td>
                        ))}
                      <td>
                        <Status value={r.status} />
                      </td>
                      <td className="muted nowrap">{date(r.updated_at)}</td>
                      <td>
                        <div className="row-actions">
                          <button
                            className="icon-button"
                            aria-label={"Lihat " + r.title}
                            onClick={() => setDetail(r)}
                          >
                            <Eye size={16} />
                          </button>
                          {editable && (
                            <>
                              <button
                                className="icon-button"
                                aria-label={"Edit " + r.title}
                                onClick={() => setEdit(r)}
                                disabled={
                                  r.data.locked ||
                                  [
                                    "attempts",
                                    "form_responses",
                                    "focus_sessions",
                                  ].includes(module.key)
                                }
                              >
                                <Pencil size={16} />
                              </button>
                              <button
                                className="icon-button danger-text"
                                aria-label={"Hapus " + r.title}
                                disabled={
                                  module.key === "focus_sessions" &&
                                  r.status !== "done"
                                }
                                onClick={() => setDeleting(r)}
                              >
                                <Trash2 size={16} />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="pagination">
              <span>
                Halaman {data.page} dari {data.pages || 1}
              </span>
              <div>
                <button
                  className="icon-button"
                  aria-label="Halaman sebelumnya"
                  disabled={page <= 1}
                  onClick={() => setPage(page - 1)}
                >
                  <ChevronLeft size={18} />
                </button>
                <button
                  className="icon-button"
                  aria-label="Halaman berikutnya"
                  disabled={page >= data.pages}
                  onClick={() => setPage(page + 1)}
                >
                  <ChevronRight size={18} />
                </button>
              </div>
            </div>
          </>
        ) : (
          <Empty
            title={"Belum ada " + module.label.toLowerCase()}
            description={
              search
                ? "Tidak ada hasil yang cocok."
                : "Tambahkan data nyata untuk memulai. Tidak ada data contoh di workspace ini."
            }
            action={
              editable &&
              !["attempts", "form_responses", "focus_sessions"].includes(
                module.key,
              ) ? (
                <button className="primary" onClick={() => setEdit({})}>
                  <Plus size={17} />
                  Tambah data pertama
                </button>
              ) : null
            }
          />
        )}
      </section>
      {edit && (
        <RecordForm
          {...context}
          record={edit}
          close={() => setEdit(null)}
          saved={() => {
            setEdit(null);
            reload();
            notice("Data berhasil disimpan di server.");
          }}
        />
      )}
      {detail && (
        <Modal title={detail.title} close={() => setDetail(null)} wide>
          <div className="record-detail">
            <Status value={detail.status} />
            <dl>
              {module.fields.map((f) => (
                <div key={f.key}>
                  <dt>{f.label}</dt>
                  <dd>
                    {f.key === "body" && detail.data.locked
                      ? "Surat terkunci sampai " +
                        dateTime(detail.data.unlock_at)
                      : displayValue(
                          f,
                          detail.data[f.key],
                          product.currency,
                          true,
                          detail.referenceNames,
                        )}
                  </dd>
                </div>
              ))}
            </dl>
            {editable && module.actions?.length > 0 && (
              <div className="workflow-actions">
                <h3>Alur kerja</h3>
                {module.actions.map((action) => (
                  <button
                    key={action}
                    className="secondary"
                    onClick={() => setActing({ action, record: detail })}
                  >
                    {actionLabels[action]}
                  </button>
                ))}
              </div>
            )}
          </div>
        </Modal>
      )}
      {deleting && (
        <Modal title="Hapus data?" close={() => setDeleting(null)}>
          <div className="modal-body">
            <p>
              {deleting.title} akan dipindahkan ke sampah dan dapat dipulihkan
              dari Pengaturan.
            </p>
            <div className="modal-footer">
              <button className="secondary" onClick={() => setDeleting(null)}>
                Batal
              </button>
              <button className="danger" onClick={remove}>
                Hapus data
              </button>
            </div>
          </div>
        </Modal>
      )}
      {acting && (
        <ActionDialog
          {...context}
          {...acting}
          close={() => setActing(null)}
          saved={() => {
            setActing(null);
            reload();
          }}
        />
      )}
    </>
  );
}
function displayValue(field, value, currency, long = false, references = {}) {
  if (value === undefined || value === null || value === "") return "—";
  if (field.type === "money") return money(value, currency);
  if (field.type === "date") return date(value);
  if (field.type === "datetime") return dateTime(value);
  if (["json", "items", "quiz"].includes(field.type))
    return long ? (
      <pre>{JSON.stringify(value, null, 2)}</pre>
    ) : (
      "Data terstruktur"
    );
  if (field.type === "ref") return references?.[value] || String(value);
  return long ? (
    <span className="pre-wrap">{String(value)}</span>
  ) : (
    String(value).slice(0, 70)
  );
}
function RecordForm({ record, module, workspace, product, close, saved }) {
  const [values, setValues] = useState(() =>
      Object.fromEntries(
        module.fields.map((f) => {
          let value =
            record.data?.[f.key] ??
            (["number", "money"].includes(f.type)
              ? ""
              : ["items", "quiz", "json"].includes(f.type)
                ? []
                : f.type === "date" && f.required
                  ? localDate()
                  : "");
          if (f.type === "money" && value !== "") value /= 100;
          if (f.type === "datetime") value = localTime(value);
          return [f.key, value];
        }),
      ),
    ),
    [status, setStatus] = useState(record.status || module.statuses[0]),
    [options, setOptions] = useState([]),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  useEffect(() => {
    if (module.fields.some((f) => ["ref", "items"].includes(f.type)))
      api(`/workspaces/${workspace.id}/options`)
        .then((d) => setOptions(d.records))
        .catch((e) => setError(e.message));
  }, []);
  const change = (key, value) => setValues((v) => ({ ...v, [key]: value }));
  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const data = { ...values, status, version: record.version };
      for (const f of module.fields) {
        const val = data[f.key];
        if (f.type === "number") {
          if (val === "") delete data[f.key];
          else data[f.key] = Number(val);
        }
        if (f.type === "money") {
          if (val === "") delete data[f.key];
          else data[f.key] = Math.round(Number(val) * 100);
        }
        if (f.type === "datetime" && val)
          data[f.key] = new Date(val).toISOString();
        if (f.type === "json" && typeof val === "string")
          data[f.key] = JSON.parse(val);
      }
      await api(
        `/workspaces/${workspace.id}/records/${module.key}` +
          (record.id ? "/" + record.id : ""),
        record.id ? "PUT" : "POST",
        data,
      );
      saved();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <Modal
      title={(record.id ? "Edit " : "Tambah ") + module.label.toLowerCase()}
      close={close}
      wide
    >
      <form className="record-form" onSubmit={submit}>
        <div className="form-grid">
          {module.fields.map((f) => (
            <label
              key={f.key}
              className={
                ["textarea", "code", "items", "quiz", "json"].includes(f.type)
                  ? "span-two"
                  : ""
              }
            >
              {f.label}
              {f.required && <span className="required">*</span>}
              {f.type === "ref" ? (
                <select
                  required={f.required}
                  value={values[f.key]}
                  onChange={(e) => change(f.key, e.target.value)}
                >
                  <option value="">Pilih {f.label.toLowerCase()}</option>
                  {options
                    .filter((o) => o.kind === f.ref)
                    .map((o) => (
                      <option key={o.id} value={o.id}>
                        {o.title}
                      </option>
                    ))}
                </select>
              ) : f.type === "select" ? (
                <select
                  value={values[f.key]}
                  onChange={(e) => change(f.key, e.target.value)}
                >
                  <option value="">Pilih…</option>
                  {f.options.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              ) : f.type === "items" ? (
                <ItemFields
                  value={values[f.key]}
                  onChange={(v) => change(f.key, v)}
                  options={options.filter((o) => o.kind === "products")}
                />
              ) : f.type === "quiz" ? (
                <QuizFields
                  value={values[f.key]}
                  onChange={(v) => change(f.key, v)}
                />
              ) : ["textarea", "code", "json"].includes(f.type) ? (
                <textarea
                  className={
                    f.type === "code" || f.type === "json" ? "code-input" : ""
                  }
                  rows={f.type === "code" ? 12 : 5}
                  required={f.required}
                  value={
                    typeof values[f.key] === "object"
                      ? JSON.stringify(values[f.key], null, 2)
                      : values[f.key]
                  }
                  onChange={(e) => change(f.key, e.target.value)}
                  spellCheck={f.type === "textarea"}
                />
              ) : (
                <input
                  type={
                    f.type === "money" || f.type === "number"
                      ? "number"
                      : f.type === "datetime"
                        ? "datetime-local"
                        : f.type === "url"
                          ? "url"
                          : f.type === "email"
                            ? "email"
                            : f.type === "color"
                              ? "color"
                              : f.type === "time"
                                ? "time"
                                : f.type === "date"
                                  ? "date"
                                  : "text"
                  }
                  min={f.type === "money" ? 0 : f.min}
                  max={f.max}
                  step={f.type === "money" ? ".01" : "any"}
                  value={values[f.key]}
                  required={f.required}
                  onChange={(e) => change(f.key, e.target.value)}
                />
              )}
            </label>
          ))}
          {!["orders", "stock_movements", "letters"].includes(module.key) && (
            <label>
              Status
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
              >
                {module.statuses.map((s) => (
                  <option key={s} value={s}>
                    {labels[s] || s}
                  </option>
                ))}
              </select>
            </label>
          )}
        </div>
        {error && <ErrorBox message={error} />}
        <div className="modal-footer">
          <button type="button" className="secondary" onClick={close}>
            Batal
          </button>
          <button className="primary" disabled={busy}>
            {busy ? (
              <Loader2 className="spin" size={18} />
            ) : (
              <Check size={18} />
            )}
            Simpan data
          </button>
        </div>
      </form>
    </Modal>
  );
}
function ItemFields({ value, onChange, options }) {
  const rows = Array.isArray(value) ? value : [];
  return (
    <div className="nested-fields">
      {rows.map((row, i) => (
        <div key={i}>
          <select
            required
            aria-label="Produk item"
            value={row.product_id}
            onChange={(e) =>
              onChange(
                rows.map((r, n) =>
                  n === i ? { ...r, product_id: e.target.value } : r,
                ),
              )
            }
          >
            <option value="">Pilih produk</option>
            {options.map((o) => (
              <option value={o.id} key={o.id}>
                {o.title}
              </option>
            ))}
          </select>
          <input
            type="number"
            min="1"
            max="100000"
            aria-label="Jumlah item"
            value={row.quantity}
            onChange={(e) =>
              onChange(
                rows.map((r, n) =>
                  n === i ? { ...r, quantity: Number(e.target.value) } : r,
                ),
              )
            }
          />
          <button
            type="button"
            className="icon-button"
            aria-label="Hapus item"
            onClick={() => onChange(rows.filter((_, n) => n !== i))}
          >
            <X size={17} />
          </button>
        </div>
      ))}
      <button
        type="button"
        className="secondary small"
        disabled={rows.length >= 20}
        onClick={() => onChange([...rows, { product_id: "", quantity: 1 }])}
      >
        <Plus size={15} />
        Tambah item
      </button>
      <small>
        Harga diambil dari produk oleh server saat pesanan disimpan.
      </small>
    </div>
  );
}
function QuizFields({ value, onChange }) {
  const rows = Array.isArray(value) ? value : [];
  const change = (i, key, v) =>
    onChange(rows.map((r, n) => (n === i ? { ...r, [key]: v } : r)));
  return (
    <div className="quiz-builder">
      {rows.map((q, i) => (
        <section key={i}>
          <strong>Pertanyaan {i + 1}</strong>
          <input
            aria-label="Pertanyaan"
            value={q.question}
            required
            onChange={(e) => change(i, "question", e.target.value)}
          />
          {q.options.map((s, j) => (
            <div key={j}>
              <input
                type="radio"
                aria-label={"Jawaban benar " + (j + 1)}
                checked={q.correct === j}
                onChange={() => change(i, "correct", j)}
              />
              <input
                aria-label={"Pilihan " + (j + 1)}
                required
                value={s}
                onChange={(e) =>
                  change(
                    i,
                    "options",
                    q.options.map((v, n) => (n === j ? e.target.value : v)),
                  )
                }
              />
            </div>
          ))}
          <button
            type="button"
            className="text-button danger-text"
            onClick={() => onChange(rows.filter((_, n) => n !== i))}
          >
            Hapus pertanyaan
          </button>
        </section>
      ))}
      <button
        type="button"
        className="secondary"
        onClick={() =>
          onChange([
            ...rows,
            { question: "", options: ["", "", "", ""], correct: 0 },
          ])
        }
      >
        <Plus size={16} />
        Tambah pertanyaan
      </button>
    </div>
  );
}
function ActionDialog({ action, record, workspace, notice, close, saved }) {
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const data = await api(
        `/workspaces/${workspace.id}/actions/${action}`,
        "POST",
        { id: record.id, ...Object.fromEntries(new FormData(e.currentTarget)) },
      );
      if (data.url) {
        await navigator.clipboard.writeText(data.url).catch(() => {});
        notice("Tautan form: " + data.url);
      } else
        notice(
          data.idempotent
            ? "Aksi ini sudah pernah diproses; tidak diulang."
            : "Workflow berhasil diproses.",
        );
      saved();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <Modal title={actionLabels[action]} close={close}>
      <form className="modal-body" onSubmit={submit}>
        <p>{record.title}</p>
        {action === "ship-order" && (
          <>
            <label>
              Kurir
              <input name="carrier" required />
            </label>
            <label>
              Nomor resi
              <input name="tracking" required />
            </label>
          </>
        )}
        {action === "invoice-order" && (
          <label>
            Jatuh tempo
            <input
              type="date"
              name="due_date"
              required
              defaultValue={localDate()}
            />
          </label>
        )}
        {action === "pay-order" && (
          <p className="callout">
            Gunakan setelah pembayaran benar-benar Anda terima. Ini mencatat
            pembayaran; tidak memindahkan uang.
          </p>
        )}
        {error && <ErrorBox message={error} />}
        <div className="modal-footer">
          <button type="button" className="secondary" onClick={close}>
            Batal
          </button>
          <button className="primary" disabled={busy}>
            Proses aksi
            <ArrowRight size={17} />
          </button>
        </div>
      </form>
    </Modal>
  );
}
function SettingsView({
  workspace,
  user,
  notice,
  auth,
  updateAuth,
  updateWorkspace,
  revision,
  refresh,
}) {
  const [members, setMembers] = useState([]),
    [trash, setTrash] = useState([]),
    [audit, setAudit] = useState([]),
    [invite, setInvite] = useState(""),
    [error, setError] = useState("");
  useEffect(() => {
    Promise.all([
      api(`/workspaces/${workspace.id}/members`),
      api(`/workspaces/${workspace.id}/trash`),
      api(`/workspaces/${workspace.id}/audit`),
    ])
      .then(([m, t, a]) => {
        setMembers(m.members);
        setTrash(t.records);
        setAudit(a.entries);
      })
      .catch((e) => setError(e.message));
  }, [workspace.id, revision]);
  const submit = (handler) => async (e) => {
    e.preventDefault();
    setError("");
    try {
      await handler(Object.fromEntries(new FormData(e.currentTarget)));
      notice("Perubahan berhasil disimpan.");
    } catch (e) {
      setError(e.message);
    }
  };
  const exportData = async () => {
    try {
      download(
        product.id + "-workspace.json",
        JSON.stringify(
          await api(`/workspaces/${workspace.id}/export`),
          null,
          2,
        ),
        "application/json",
      );
    } catch (e) {
      setError(e.message);
    }
  };
  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">WORKSPACE CONTROL</p>
          <h1>Pengaturan</h1>
          <p>Akun, anggota, akses, dan data workspace.</p>
        </div>
        <button className="secondary" onClick={exportData}>
          <Download size={17} />
          Backup data JSON
        </button>
      </div>
      {error && <ErrorBox message={error} />}
      <div className="settings-grid">
        <section className="panel settings-card">
          <h2>Profil akun</h2>
          <form
            onSubmit={submit(async (f) => {
              const d = await api("/auth/profile", "PATCH", f);
              updateAuth((v) => ({ ...v, user: d.user }));
            })}
          >
            <label>
              Nama
              <input
                name="name"
                defaultValue={user.name}
                required
                maxLength={80}
              />
            </label>
            <label>
              Email
              <input value={user.email} disabled readOnly />
            </label>
            <button className="primary small">Simpan profil</button>
          </form>
        </section>
        <section className="panel settings-card">
          <h2>Ubah password</h2>
          <form
            onSubmit={submit(async (f) => {
              await api("/auth/password", "POST", f);
            })}
          >
            <label>
              Password saat ini
              <input
                type="password"
                name="current"
                required
                autoComplete="current-password"
              />
            </label>
            <label>
              Password baru
              <input
                type="password"
                name="password"
                required
                minLength={12}
                autoComplete="new-password"
              />
            </label>
            <small>Session lain akan dicabut setelah perubahan.</small>
            <button className="primary small">Ubah password</button>
          </form>
        </section>
      </div>
      {workspace.role === "owner" && (
        <div className="settings-grid">
          <section className="panel settings-card">
            <h2>Nama workspace</h2>
            <form
              onSubmit={submit(async (f) => {
                const d = await api(`/workspaces/${workspace.id}`, "PATCH", f);
                updateWorkspace(d.workspace);
                updateAuth((v) => ({
                  ...v,
                  workspaces: v.workspaces.map((w) =>
                    w.id === workspace.id
                      ? { ...w, name: d.workspace.name }
                      : w,
                  ),
                }));
              })}
            >
              <label>
                Nama
                <input name="name" defaultValue={workspace.name} required />
              </label>
              <button className="primary small">Simpan</button>
            </form>
          </section>
          <section className="panel settings-card">
            <h2>Undang anggota</h2>
            <form
              onSubmit={submit(async (f) => {
                const d = await api(
                  `/workspaces/${workspace.id}/invitations`,
                  "POST",
                  f,
                );
                setInvite(d.url);
              })}
            >
              <label>
                Email tujuan
                <input type="email" name="email" required />
              </label>
              <label>
                Peran
                <select name="role">
                  <option value="editor">Editor — baca dan ubah data</option>
                  <option value="viewer">Viewer — baca data</option>
                </select>
              </label>
              <button className="primary small">Buat tautan undangan</button>
            </form>
            {invite && (
              <div className="callout">
                <p>
                  Bagikan tautan ini kepada pemilik email tujuan. Berlaku tujuh
                  hari.
                </p>
                <input readOnly value={invite} />
                <button
                  className="text-button"
                  onClick={() =>
                    navigator.clipboard
                      .writeText(invite)
                      .then(() => notice("Tautan disalin."))
                      .catch(() =>
                        setError(
                          "Tidak dapat menyalin; salin tautan secara manual.",
                        ),
                      )
                  }
                >
                  Salin tautan
                </button>
              </div>
            )}
          </section>
        </div>
      )}
      <section className="panel settings-card">
        <h2>Buat workspace baru</h2>
        <p>Pisahkan data tim yang memiliki anggota atau hak akses berbeda.</p>
        <form
          onSubmit={submit(async (f) => {
            const d = await api("/workspaces", "POST", f);
            updateAuth((v) => ({
              ...v,
              workspaces: [...v.workspaces, d.workspace],
            }));
            updateWorkspace(d.workspace);
          })}
        >
          <label>
            Nama workspace baru
            <input name="name" required maxLength={100} />
          </label>
          <button className="primary small">Buat workspace kosong</button>
        </form>
      </section>
      <section className="panel settings-card">
        <h2>Anggota workspace</h2>
        <p>
          Anggota memiliki akses ke seluruh bidang di ruang ini sesuai perannya.
          Buat ruang terpisah untuk tim atau data yang perlu dibatasi.
        </p>
        <div className="member-list">
          {members.map((m) => (
            <div key={m.id}>
              <span className="avatar">{m.name.slice(0, 2).toUpperCase()}</span>
              <span>
                <strong>{m.name}</strong>
                <small>{m.email}</small>
              </span>
              {workspace.role === "owner" && m.role !== "owner" ? (
                <select
                  aria-label={"Peran " + m.name}
                  value={m.role}
                  onChange={(e) =>
                    api(`/workspaces/${workspace.id}/members`, "PATCH", {
                      id: m.id,
                      role: e.target.value,
                    })
                      .then(refresh)
                      .catch((e) => setError(e.message))
                  }
                >
                  <option value="editor">editor</option>
                  <option value="viewer">viewer</option>
                </select>
              ) : (
                <span className="pill">{m.role}</span>
              )}
              {workspace.role === "owner" && m.role !== "owner" && (
                <button
                  className="text-button danger-text"
                  onClick={() =>
                    api(`/workspaces/${workspace.id}/members/${m.id}`, "DELETE")
                      .then(() => {
                        refresh();
                        notice("Akses anggota dicabut.");
                      })
                      .catch((e) => setError(e.message))
                  }
                >
                  Cabut akses
                </button>
              )}
            </div>
          ))}
        </div>
      </section>
      <section className="panel settings-card">
        <h2>Sampah</h2>
        <p>Data yang dihapus dapat dipulihkan di sini.</p>
        {trash.length ? (
          <div className="recent-list">
            {trash.map((r) => (
              <div key={r.id}>
                <FileText size={18} />
                <span>
                  <strong>{r.title}</strong>
                  <small>{dateTime(r.deleted_at)}</small>
                </span>
                {workspace.role !== "viewer" && (
                  <button
                    className="secondary small"
                    onClick={() =>
                      api(
                        `/workspaces/${workspace.id}/restore/${r.id}`,
                        "POST",
                        {},
                      )
                        .then(() => {
                          refresh();
                          notice("Data dipulihkan.");
                        })
                        .catch((e) => setError(e.message))
                    }
                  >
                    Pulihkan
                  </button>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="muted">Sampah kosong.</p>
        )}
      </section>
      <section className="panel settings-card">
        <h2>Audit perubahan</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Waktu</th>
                <th>Pelaku</th>
                <th>Aksi</th>
                <th>Detail</th>
              </tr>
            </thead>
            <tbody>
              {audit.map((a) => (
                <tr key={a.id}>
                  <td>{dateTime(a.created_at)}</td>
                  <td>{a.actor}</td>
                  <td>{a.action}</td>
                  <td>{a.detail || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

export {
  Auth,
  Recovery,
  Onboarding,
  Records,
  RecordForm,
  SettingsView,
  ToolBoundary,
  Brand,
};
