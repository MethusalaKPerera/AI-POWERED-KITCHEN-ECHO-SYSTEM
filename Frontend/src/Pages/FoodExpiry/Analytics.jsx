// src/Pages/FoodExpiry/Analytics.jsx
import React, { useEffect, useMemo, useState } from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import "./foodexpiry.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

function cx(...arr) {
  return arr.filter(Boolean).join(" ");
}

function clamp(n, a, b) {
  return Math.max(a, Math.min(b, n));
}

function niceDate(ts) {
  if (!ts) return "-";
  // ts like 2026-02-10T10:12:33.123Z
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return String(ts).slice(0, 10);
  return d.toISOString().slice(0, 10);
}

function downloadFile(url, filenameHint) {
  // Works for CSV/PDF from Flask endpoints
  const a = document.createElement("a");
  a.href = url;
  if (filenameHint) a.download = filenameHint;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

export default function Analytics() {
  // ✅ userId (keep same behavior you use elsewhere: localStorage fallback)
  const [userId, setUserId] = useState(() => localStorage.getItem("FE_USER_ID") || "U001");

  // Filters
  const [period, setPeriod] = useState("30d"); // 7d | 30d | custom
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");

  const [item, setItem] = useState("all");
  const [storage, setStorage] = useState("all");

  // Options
  const [itemsList, setItemsList] = useState([]);
  const storageOptions = useMemo(() => ["all", "fridge", "freezer", "pantry"], []);

  // Data
  const [summary, setSummary] = useState(null);
  const [series, setSeries] = useState([]);
  const [history, setHistory] = useState([]);
  const [total, setTotal] = useState(0);

  // UI
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [err, setErr] = useState("");

  // Table pagination
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);

  // Expand row (interactive)
  const [expandedIdx, setExpandedIdx] = useState(null);

  // Hover effects (lightweight)
  const hoverCardStyle = {
    transition: "transform .15s ease, box-shadow .15s ease, border-color .15s ease",
  };

  // Persist user id
  useEffect(() => {
    localStorage.setItem("FE_USER_ID", userId);
  }, [userId]);

  // Load item options
  useEffect(() => {
    let ignore = false;
    (async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/food/options`);
        const data = await res.json();
        if (!ignore) setItemsList(Array.isArray(data.items) ? data.items : []);
      } catch {
        // ignore
      }
    })();
    return () => {
      ignore = true;
    };
  }, []);

  const queryParams = useMemo(() => {
    const p = new URLSearchParams();
    p.set("user_id", userId.trim());
    p.set("item", item);
    p.set("storage", storage);

    if (period === "custom") {
      if (start) p.set("start", start);
      if (end) p.set("end", end);
    } else {
      p.set("period", period); // 7d or 30d
    }

    return p.toString();
  }, [userId, item, storage, period, start, end]);

  async function loadSummaryAndSeries() {
    setErr("");
    setLoading(true);
    setExpandedIdx(null);

    try {
      const [sumRes, tsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/food/analytics/summary?${queryParams}`),
        fetch(`${API_BASE_URL}/api/food/analytics/timeseries?${queryParams}`),
      ]);

      const sumJson = await sumRes.json();
      const tsJson = await tsRes.json();

      if (!sumRes.ok) throw new Error(sumJson?.error || sumJson?.message || "Failed to load analytics summary");
      if (!tsRes.ok) throw new Error(tsJson?.error || tsJson?.message || "Failed to load analytics timeseries");

      setSummary(sumJson);
      setSeries(Array.isArray(tsJson.series) ? tsJson.series : []);
    } catch (e) {
      setSummary(null);
      setSeries([]);
      setErr(String(e?.message || e));
    } finally {
      setLoading(false);
    }
  }

  async function loadHistory(nextPage = page, nextPageSize = pageSize) {
    setErr("");
    setLoadingHistory(true);
    setExpandedIdx(null);

    try {
      const p = new URLSearchParams(queryParams);
      p.set("page", String(nextPage));
      p.set("page_size", String(nextPageSize));

      const res = await fetch(`${API_BASE_URL}/api/food/analytics/history?${p.toString()}`);
      const json = await res.json();

      if (!res.ok) throw new Error(json?.error || json?.message || "Failed to load history");

      setHistory(Array.isArray(json.rows) ? json.rows : []);
      setTotal(Number(json.total || 0));
    } catch (e) {
      setHistory([]);
      setTotal(0);
      setErr(String(e?.message || e));
    } finally {
      setLoadingHistory(false);
    }
  }

  useEffect(() => {
    // reset table on filter changes
    setPage(1);
    loadSummaryAndSeries();
    loadHistory(1, pageSize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [queryParams]);

  const maxPage = useMemo(() => {
    if (!total) return 1;
    return Math.max(1, Math.ceil(total / pageSize));
  }, [total, pageSize]);

  const kpis = summary?.kpis || {};
  const urgency = summary?.urgency_distribution || {};
  const personalization = summary?.personalization || {};

  const urgencyCards = useMemo(() => {
    const map = [
      { key: "expired", label: "Expired", hint: "< 0 days" },
      { key: "0-3", label: "Urgent", hint: "0–3 days" },
      { key: "4-7", label: "Soon", hint: "4–7 days" },
      { key: "8+", label: "Safe", hint: "8+ days" },
    ];
    return map.map((m) => ({
      ...m,
      value: urgency?.[m.key] ?? 0,
    }));
  }, [urgency]);

  const topInsights = useMemo(() => {
    const totalPred = Number(kpis.total_predictions || 0);
    const personalized = Number(kpis.personalized_predictions || 0);
    const caps = Number(kpis.printed_caps_applied || 0);
    const avgAED = Number(kpis.avg_aed_delta_days || 0);

    const pct = totalPred ? Math.round((personalized / totalPred) * 100) : 0;

    return [
      { title: "Personalization Usage", value: `${pct}%`, sub: `${personalized}/${totalPred} predictions` },
      { title: "Printed Expiry Safety Caps", value: String(caps), sub: "Times the model was capped" },
      { title: "Avg AED Delta", value: `${avgAED.toFixed(2)} days`, sub: "Personalized − Baseline" },
    ];
  }, [kpis]);

  const chartData = useMemo(() => {
    // Normalize series for display
    return (series || []).map((d) => ({
      date: d.date,
      predictions: Number(d.predictions || 0),
      avg_scp: d.avg_scp == null ? null : Number(d.avg_scp),
      urgent_count: Number(d.urgent_count || 0),
      expired_count: Number(d.expired_count || 0),
      avg_baseline_days: d.avg_baseline_days == null ? null : Number(d.avg_baseline_days),
      avg_personalized_days: d.avg_personalized_days == null ? null : Number(d.avg_personalized_days),
    }));
  }, [series]);

  // ✅ Lightweight charts without extra libs (CSS bars)
  function MiniBar({ value, max = 10 }) {
    const pct = max ? clamp((value / max) * 100, 0, 100) : 0;
    return (
      <div className="fe-minibar" style={{ height: 10, background: "#eaf5f1", borderRadius: 999, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: "#2fbf9b" }} />
      </div>
    );
  }

  function SparkBars({ data, keyName }) {
    const vals = (data || []).map((x) => Number(x?.[keyName] || 0));
    const max = Math.max(1, ...vals);
    return (
      <div style={{ display: "flex", gap: 6, alignItems: "flex-end", height: 56 }}>
        {vals.slice(-14).map((v, i) => (
          <div
            key={i}
            title={`${v}`}
            style={{
              width: 10,
              height: `${clamp((v / max) * 100, 4, 100)}%`,
              background: "#0ea5e9",
              borderRadius: 6,
              opacity: 0.85,
              transition: "transform .15s ease",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.transform = "translateY(-2px)")}
            onMouseLeave={(e) => (e.currentTarget.style.transform = "translateY(0px)")}
          />
        ))}
      </div>
    );
  }

  const exportCsvUrl = `${API_BASE_URL}/api/food/analytics/export/csv?${queryParams}`;
  const exportPdfUrl = `${API_BASE_URL}/api/food/analytics/export/pdf?${queryParams}`;

  return (
    <div className="fe-page">
      <Sidebar />
      <div className="fe-main">
        <Topbar />

        {/* ========= HERO HEADER (make it bold + breathable) ========= */}
        <div className="fe-hero">
          <div className="fe-hero__left">
            <h1 className="fe-title" style={{ fontWeight: 900, letterSpacing: 0.2 }}>
              📊 User Analytics
            </h1>
            <p className="fe-subtitle" style={{ fontWeight: 600, marginTop: 6 }}>
              Track prediction history, urgency trends, personalization status, and download reports.
            </p>
          </div>

          <div className="fe-hero__right">
            <div className="fe-chip" title="Active user">
              <b>User:</b>&nbsp;{userId || "-"}
            </div>
            <div className="fe-chip" title="Active filter">
              <b>Range:</b>&nbsp;{period === "custom" ? `${start || "?"} → ${end || "?"}` : period}
            </div>
          </div>
        </div>

        {/* ========= FILTER BAR (hover containers) ========= */}
        <div className="fe-grid" style={{ marginTop: 14 }}>
          <div
            className="fe-card"
            style={{
              ...hoverCardStyle,
              border: "1px solid rgba(34, 197, 160, .15)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 12px 30px rgba(0,0,0,.08)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0px)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <div className="fe-card__header">
              <h2 style={{ margin: 0, fontWeight: 900 }}>Filters</h2>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <button
                  className="fe-btn fe-btn--ghost"
                  onClick={() => {
                    setItem("all");
                    setStorage("all");
                    setPeriod("30d");
                    setStart("");
                    setEnd("");
                  }}
                  title="Reset filters"
                >
                  Reset
                </button>

                <button
                  className="fe-btn"
                  onClick={() => {
                    loadSummaryAndSeries();
                    loadHistory(1, pageSize);
                  }}
                  title="Refresh analytics"
                >
                  Refresh
                </button>

                <button
                  className="fe-btn fe-btn--outline"
                  onClick={() => downloadFile(exportCsvUrl, `food_expiry_history_${userId}.csv`)}
                  title="Download CSV history"
                >
                  Download CSV
                </button>

                <button
                  className="fe-btn fe-btn--outline"
                  onClick={() => downloadFile(exportPdfUrl, `food_expiry_report_${userId}.pdf`)}
                  title="Download PDF report (requires reportlab in backend)"
                >
                  Download PDF
                </button>
              </div>
            </div>

            <div className="fe-card__content">
              <div className="fe-form-grid">
                <div className="fe-field">
                  <label className="fe-label">
                    <b>User ID</b>
                  </label>
                  <input
                    className="fe-input"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    placeholder="U001"
                  />
                  <div className="fe-help">Tip: use the same userId you used in AddFood / Inventory.</div>
                </div>

                <div className="fe-field">
                  <label className="fe-label">
                    <b>Item</b>
                  </label>
                  <select className="fe-select" value={item} onChange={(e) => setItem(e.target.value)}>
                    <option value="all">All items</option>
                    {itemsList.map((x) => (
                      <option key={x} value={x}>
                        {x}
                      </option>
                    ))}
                  </select>
                  <div className="fe-help">Filter analytics for a specific food item.</div>
                </div>

                <div className="fe-field">
                  <label className="fe-label">
                    <b>Storage</b>
                  </label>
                  <select className="fe-select" value={storage} onChange={(e) => setStorage(e.target.value)}>
                    {storageOptions.map((s) => (
                      <option key={s} value={s}>
                        {s === "all" ? "All storages" : s}
                      </option>
                    ))}
                  </select>
                  <div className="fe-help">Compare how fridge/freezer/pantry behaves.</div>
                </div>

                <div className="fe-field">
                  <label className="fe-label">
                    <b>Period</b>
                  </label>
                  <select
                    className="fe-select"
                    value={period}
                    onChange={(e) => {
                      setPeriod(e.target.value);
                      if (e.target.value !== "custom") {
                        setStart("");
                        setEnd("");
                      }
                    }}
                  >
                    <option value="7d">Last 7 days</option>
                    <option value="30d">Last 30 days</option>
                    <option value="custom">Custom range</option>
                  </select>
                  <div className="fe-help">Pick a time window for insights.</div>
                </div>

                {period === "custom" && (
                  <>
                    <div className="fe-field">
                      <label className="fe-label">
                        <b>Start</b>
                      </label>
                      <input className="fe-input" type="date" value={start} onChange={(e) => setStart(e.target.value)} />
                    </div>
                    <div className="fe-field">
                      <label className="fe-label">
                        <b>End</b>
                      </label>
                      <input className="fe-input" type="date" value={end} onChange={(e) => setEnd(e.target.value)} />
                    </div>
                  </>
                )}
              </div>

              {!!err && (
                <div className="fe-alert fe-alert--error" style={{ marginTop: 12 }}>
                  <b>Error:</b>&nbsp;{err}
                  <div style={{ marginTop: 6, opacity: 0.9 }}>
                    If you clicked <b>Download PDF</b> and you see a server error, install backend dependency:
                    <code style={{ marginLeft: 8 }}>pip install reportlab</code>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ========= KPI CARDS ========= */}
        <div className="fe-grid fe-grid--cards" style={{ marginTop: 14 }}>
          <div
            className="fe-card"
            style={hoverCardStyle}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 12px 30px rgba(0,0,0,.08)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0px)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <div className="fe-card__content">
              <div className="fe-kpi">
                <div className="fe-kpi__title">
                  <b>Total Predictions</b>
                </div>
                <div className="fe-kpi__value">{loading ? "…" : kpis.total_predictions ?? 0}</div>
                <div className="fe-kpi__sub">All predictions stored in predictionHistory.</div>
              </div>
            </div>
          </div>

          <div
            className="fe-card"
            style={hoverCardStyle}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 12px 30px rgba(0,0,0,.08)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0px)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <div className="fe-card__content">
              <div className="fe-kpi">
                <div className="fe-kpi__title">
                  <b>Feedback Count</b>
                </div>
                <div className="fe-kpi__value">{loading ? "…" : kpis.total_feedback_count ?? 0}</div>
                <div className="fe-kpi__sub">How much your model has learned so far.</div>
              </div>
            </div>
          </div>

          <div
            className="fe-card"
            style={hoverCardStyle}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 12px 30px rgba(0,0,0,.08)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0px)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <div className="fe-card__content">
              <div className="fe-kpi">
                <div className="fe-kpi__title">
                  <b>Personalization Ready</b>
                </div>
                <div className="fe-kpi__value">
                  {loading ? "…" : personalization?.personalization_ready == null ? "—" : personalization.personalization_ready ? "YES" : "NO"}
                </div>
                <div className="fe-kpi__sub">
                  {item === "all"
                    ? "Select an item to see readiness."
                    : `Needs ${personalization?.min_feedback_required ?? 5} feedbacks per item.`}
                </div>
              </div>

              {item !== "all" && (
                <div style={{ marginTop: 10 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 6 }}>
                    <span>
                      <b>Item Feedback</b>
                    </span>
                    <span>
                      {(personalization?.item_feedback_count ?? 0)}/{personalization?.min_feedback_required ?? 5}
                    </span>
                  </div>
                  <MiniBar value={personalization?.item_feedback_count ?? 0} max={personalization?.min_feedback_required ?? 5} />
                  <div className="fe-help" style={{ marginTop: 6 }}>
                    {personalization?.feedback_needed ? (
                      <>
                        Add <b>{personalization.feedback_needed}</b> more feedback(s) for this item to activate AED.
                      </>
                    ) : (
                      <>
                        AED personalization is <b>active</b> for this item.
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ========= URGENCY + TRENDS ========= */}
        <div className="fe-grid" style={{ marginTop: 14 }}>
          <div
            className="fe-card"
            style={hoverCardStyle}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 12px 30px rgba(0,0,0,.08)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0px)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <div className="fe-card__header">
              <h2 style={{ margin: 0, fontWeight: 900 }}>Urgency Overview</h2>
              <div className="fe-help">Based on days_left bucket counts from prediction history.</div>
            </div>

            <div className="fe-card__content">
              <div className="fe-urgency-grid">
                {urgencyCards.map((u) => (
                  <div
                    key={u.key}
                    className="fe-urgency"
                    title={`${u.label} (${u.hint})`}
                    style={{
                      border: "1px solid rgba(0,0,0,.06)",
                      borderRadius: 14,
                      padding: 12,
                      transition: "transform .15s ease, box-shadow .15s ease",
                      cursor: "default",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = "translateY(-2px)";
                      e.currentTarget.style.boxShadow = "0 10px 24px rgba(0,0,0,.08)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = "translateY(0px)";
                      e.currentTarget.style.boxShadow = "none";
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                      <div style={{ fontWeight: 900 }}>{u.label}</div>
                      <div style={{ fontWeight: 900, fontSize: 20 }}>{loading ? "…" : u.value}</div>
                    </div>
                    <div className="fe-help">{u.hint}</div>
                  </div>
                ))}
              </div>

              <div style={{ marginTop: 14 }}>
                <h3 style={{ margin: "0 0 8px 0", fontWeight: 900 }}>Quick Trend (Predictions per day)</h3>
                <div
                  className="fe-hoverbox"
                  style={{
                    borderRadius: 14,
                    padding: 12,
                    border: "1px solid rgba(34, 197, 160, .15)",
                    background: "linear-gradient(180deg, rgba(14,165,233,.10), rgba(47,191,155,.08))",
                  }}
                >
                  <SparkBars data={chartData} keyName="predictions" />
                  <div className="fe-help" style={{ marginTop: 8 }}>
                    Hover bars for counts. Use filters above to compare item/storage.
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div
            className="fe-card"
            style={hoverCardStyle}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 12px 30px rgba(0,0,0,.08)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0px)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <div className="fe-card__header">
              <h2 style={{ margin: 0, fontWeight: 900 }}>Insights</h2>
              <div className="fe-help">High-level interpretation of your behavior & model outputs.</div>
            </div>

            <div className="fe-card__content">
              <div className="fe-insights">
                {topInsights.map((x) => (
                  <div
                    key={x.title}
                    style={{
                      border: "1px solid rgba(0,0,0,.06)",
                      borderRadius: 14,
                      padding: 12,
                      transition: "transform .15s ease, box-shadow .15s ease",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = "translateY(-2px)";
                      e.currentTarget.style.boxShadow = "0 10px 24px rgba(0,0,0,.08)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = "translateY(0px)";
                      e.currentTarget.style.boxShadow = "none";
                    }}
                  >
                    <div style={{ fontWeight: 900 }}>{x.title}</div>
                    <div style={{ fontSize: 22, fontWeight: 900, marginTop: 6 }}>{loading ? "…" : x.value}</div>
                    <div className="fe-help">{x.sub}</div>
                  </div>
                ))}
              </div>

              <div style={{ marginTop: 14 }}>
                <h3 style={{ margin: "0 0 8px 0", fontWeight: 900 }}>Daily Signals (last points)</h3>
                <div className="fe-table-wrap">
                  <table className="fe-table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Predictions</th>
                        <th>Urgent (0–3)</th>
                        <th>Expired</th>
                        <th>Avg SCP</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(chartData || []).slice(-8).reverse().map((d) => (
                        <tr key={d.date}>
                          <td>
                            <b>{d.date}</b>
                          </td>
                          <td>{d.predictions}</td>
                          <td>{d.urgent_count}</td>
                          <td>{d.expired_count}</td>
                          <td>{d.avg_scp == null ? "-" : d.avg_scp}</td>
                        </tr>
                      ))}
                      {!chartData?.length && (
                        <tr>
                          <td colSpan={5} style={{ opacity: 0.7 }}>
                            No timeseries data yet (make some predictions first).
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>

                <div className="fe-help" style={{ marginTop: 8 }}>
                  This view is built from <b>/analytics/timeseries</b>.
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ========= HISTORY TABLE ========= */}
        <div className="fe-grid" style={{ marginTop: 14 }}>
          <div
            className="fe-card"
            style={hoverCardStyle}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 12px 30px rgba(0,0,0,.08)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0px)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <div className="fe-card__header">
              <h2 style={{ margin: 0, fontWeight: 900 }}>Prediction History</h2>

              <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
                <div className="fe-chip">
                  <b>Total:</b>&nbsp;{total}
                </div>

                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <span className="fe-help">
                    <b>Rows:</b>
                  </span>
                  <select
                    className="fe-select"
                    value={pageSize}
                    onChange={(e) => {
                      const next = Number(e.target.value || 25);
                      setPageSize(next);
                      setPage(1);
                      loadHistory(1, next);
                    }}
                    style={{ width: 110 }}
                  >
                    {[10, 25, 50, 100].map((n) => (
                      <option key={n} value={n}>
                        {n}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  className="fe-btn fe-btn--ghost"
                  disabled={page <= 1 || loadingHistory}
                  onClick={() => {
                    const next = Math.max(1, page - 1);
                    setPage(next);
                    loadHistory(next, pageSize);
                  }}
                >
                  ◀ Prev
                </button>

                <div className="fe-chip" title="Current page">
                  <b>Page:</b>&nbsp;{page}/{maxPage}
                </div>

                <button
                  className="fe-btn fe-btn--ghost"
                  disabled={page >= maxPage || loadingHistory}
                  onClick={() => {
                    const next = Math.min(maxPage, page + 1);
                    setPage(next);
                    loadHistory(next, pageSize);
                  }}
                >
                  Next ▶
                </button>
              </div>
            </div>

            <div className="fe-card__content">
              <div className="fe-help" style={{ marginBottom: 10 }}>
                Click a row to expand more details (interactive).
              </div>

              <div className="fe-table-wrap">
                <table className="fe-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Item</th>
                      <th>Storage</th>
                      <th>Final Expiry</th>
                      <th>Days Left</th>
                      <th>SCP</th>
                      <th>AED</th>
                      <th>Cap</th>
                    </tr>
                  </thead>

                  <tbody>
                    {loadingHistory && (
                      <tr>
                        <td colSpan={8} style={{ padding: 14, opacity: 0.75 }}>
                          Loading history…
                        </td>
                      </tr>
                    )}

                    {!loadingHistory && history.map((r, idx) => {
                      const expanded = expandedIdx === idx;
                      const daysLeft = r.days_left;
                      const daysLeftNum = daysLeft == null ? null : Number(daysLeft);

                      let badge = "safe";
                      if (daysLeftNum != null && daysLeftNum < 0) badge = "expired";
                      else if (daysLeftNum != null && daysLeftNum <= 3) badge = "urgent";
                      else if (daysLeftNum != null && daysLeftNum <= 7) badge = "soon";

                      return (
                        <React.Fragment key={`${r.ts}-${idx}`}>
                          <tr
                            className={cx("fe-row-click", expanded && "is-open")}
                            style={{ cursor: "pointer" }}
                            onClick={() => setExpandedIdx(expanded ? null : idx)}
                            title="Click to expand"
                          >
                            <td>
                              <b>{niceDate(r.ts)}</b>
                            </td>
                            <td style={{ fontWeight: 800 }}>{r.item_name || "-"}</td>
                            <td>{r.storage_type || "-"}</td>
                            <td>{r.final_expiry_date || "-"}</td>
                            <td>
                              <span className={cx("fe-pill", `fe-pill--${badge}`)}>{daysLeftNum == null ? "-" : daysLeftNum}</span>
                            </td>
                            <td>{r.scp == null ? "-" : Number(r.scp).toFixed(2)}</td>
                            <td>{r.personalization_enabled ? "✅" : "—"}</td>
                            <td>{r.printed_cap_applied ? "✅" : "—"}</td>
                          </tr>

                          {expanded && (
                            <tr>
                              <td colSpan={8} style={{ background: "rgba(14,165,233,.06)" }}>
                                <div
                                  style={{
                                    padding: 12,
                                    borderRadius: 14,
                                    border: "1px solid rgba(14,165,233,.18)",
                                    background: "rgba(255,255,255,.6)",
                                  }}
                                >
                                  <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
                                    <div className="fe-chip">
                                      <b>FoodId:</b>&nbsp;{r.foodId || "-"}
                                    </div>
                                    <div className="fe-chip">
                                      <b>Category:</b>&nbsp;{r.category || "-"}
                                    </div>
                                    <div className="fe-chip">
                                      <b>Baseline Days:</b>&nbsp;{r.baseline_days ?? "-"}
                                    </div>
                                    <div className="fe-chip">
                                      <b>Personalized Days:</b>&nbsp;{r.personalized_days ?? "-"}
                                    </div>
                                    <div className="fe-chip">
                                      <b>Printed Expiry:</b>&nbsp;{r.printed_expiry_date || "-"}
                                    </div>
                                  </div>

                                  <div style={{ marginTop: 10, display: "flex", gap: 10, flexWrap: "wrap" }}>
                                    <button
                                      className="fe-btn fe-btn--outline"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        // Export focused (same backend supports item filter only; for single row use item+storage+custom range = that date)
                                        const d = niceDate(r.ts);
                                        const p = new URLSearchParams(queryParams);
                                        p.set("item", (r.item_name || "all").toLowerCase());
                                        p.set("storage", (r.storage_type || "all").toLowerCase());
                                        p.set("start", d);
                                        p.set("end", d);
                                        p.set("period", ""); // ignore
                                        downloadFile(`${API_BASE_URL}/api/food/analytics/export/csv?${p.toString()}`, `history_${userId}_${d}.csv`);
                                      }}
                                      title="Download CSV for this row's date/item/storage"
                                    >
                                      Export CSV (This)
                                    </button>

                                    <button
                                      className="fe-btn fe-btn--outline"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        const d = niceDate(r.ts);
                                        const p = new URLSearchParams(queryParams);
                                        p.set("item", (r.item_name || "all").toLowerCase());
                                        p.set("storage", (r.storage_type || "all").toLowerCase());
                                        p.set("start", d);
                                        p.set("end", d);
                                        p.set("period", "");
                                        downloadFile(`${API_BASE_URL}/api/food/analytics/export/pdf?${p.toString()}`, `report_${userId}_${d}.pdf`);
                                      }}
                                      title="Download PDF for this row's date/item/storage (requires reportlab)"
                                    >
                                      Export PDF (This)
                                    </button>
                                  </div>

                                  <div className="fe-help" style={{ marginTop: 10 }}>
                                    This expanded view is for user clarity (history evidence for panel + research report).
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })}

                    {!loadingHistory && !history.length && (
                      <tr>
                        <td colSpan={8} style={{ padding: 14, opacity: 0.75 }}>
                          No history found for these filters. Try predicting some items first.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div className="fe-help" style={{ marginTop: 10 }}>
                Backend endpoints used: <b>/analytics/summary</b>, <b>/analytics/timeseries</b>, <b>/analytics/history</b>,{" "}
                <b>/analytics/export/csv</b>, <b>/analytics/export/pdf</b>.
              </div>
            </div>
          </div>
        </div>

        {/* ========= tiny styling helpers if your CSS doesn't have these ========= */}
        <style>{`
          .fe-hero{
            display:flex; align-items:flex-start; justify-content:space-between; gap:14px;
            padding: 14px 14px;
            border-radius: 16px;
            background: linear-gradient(180deg, rgba(47,191,155,.12), rgba(14,165,233,.08));
            border: 1px solid rgba(34,197,160,.18);
          }
          .fe-hero__right{ display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end; }
          .fe-title{ margin:0; }
          .fe-subtitle{ margin:0; opacity:.85; }
          .fe-form-grid{ display:grid; grid-template-columns: repeat(3, minmax(220px, 1fr)); gap: 12px; }
          @media (max-width: 1100px){ .fe-form-grid{ grid-template-columns: repeat(2, minmax(220px, 1fr)); } }
          @media (max-width: 760px){ .fe-form-grid{ grid-template-columns: 1fr; } }
          .fe-field{ display:flex; flex-direction:column; gap:6px; }
          .fe-label{ font-size: 13px; opacity:.9; }
          .fe-help{ font-size: 12px; opacity:.75; }
          .fe-grid{ display:block; }
          .fe-grid--cards{ display:grid; grid-template-columns: repeat(3, minmax(220px, 1fr)); gap: 12px; }
          @media (max-width: 980px){ .fe-grid--cards{ grid-template-columns: 1fr; } }
          .fe-urgency-grid{ display:grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 10px; }
          @media (max-width: 980px){ .fe-urgency-grid{ grid-template-columns: repeat(2, minmax(140px, 1fr)); } }
          @media (max-width: 520px){ .fe-urgency-grid{ grid-template-columns: 1fr; } }
          .fe-insights{ display:grid; grid-template-columns: repeat(3, minmax(180px, 1fr)); gap: 10px; }
          @media (max-width: 980px){ .fe-insights{ grid-template-columns: 1fr; } }
          .fe-card__header{ display:flex; justify-content:space-between; align-items:flex-start; gap:12px; flex-wrap:wrap; }
          .fe-card__content{ margin-top: 10px; }
          .fe-chip{
            display:inline-flex; align-items:center; gap:6px;
            border: 1px solid rgba(0,0,0,.08);
            border-radius: 999px;
            padding: 8px 12px;
            background: rgba(255,255,255,.65);
          }
          .fe-kpi__title{ font-size: 13px; opacity:.85; }
          .fe-kpi__value{ font-size: 30px; font-weight: 900; margin-top: 6px; }
          .fe-kpi__sub{ font-size: 12px; opacity:.75; margin-top: 4px; }
          .fe-table-wrap{ overflow:auto; border-radius: 14px; border: 1px solid rgba(0,0,0,.06); }
          .fe-table{ width:100%; border-collapse: collapse; background: rgba(255,255,255,.75); }
          .fe-table th, .fe-table td{ padding: 10px 10px; border-bottom: 1px solid rgba(0,0,0,.06); text-align:left; font-size: 13px; }
          .fe-row-click:hover{ background: rgba(47,191,155,.08); }
          .fe-pill{
            display:inline-flex; align-items:center; justify-content:center;
            min-width: 52px;
            padding: 4px 10px;
            border-radius: 999px;
            font-weight: 900;
            border: 1px solid rgba(0,0,0,.08);
            background: rgba(255,255,255,.8);
          }
          .fe-pill--expired{ background: rgba(239,68,68,.12); border-color: rgba(239,68,68,.25); }
          .fe-pill--urgent{ background: rgba(245,158,11,.14); border-color: rgba(245,158,11,.28); }
          .fe-pill--soon{ background: rgba(14,165,233,.14); border-color: rgba(14,165,233,.28); }
          .fe-pill--safe{ background: rgba(34,197,94,.12); border-color: rgba(34,197,94,.25); }
          .fe-alert{ padding: 12px; border-radius: 14px; border: 1px solid rgba(239,68,68,.28); background: rgba(239,68,68,.08); }
          .fe-btn{
            border: none;
            padding: 9px 12px;
            border-radius: 12px;
            background: #10b981;
            color: #fff;
            font-weight: 900;
            cursor: pointer;
            transition: transform .12s ease, filter .12s ease;
          }
          .fe-btn:hover{ transform: translateY(-1px); filter: brightness(1.05); }
          .fe-btn:disabled{ opacity:.55; cursor:not-allowed; transform:none; }
          .fe-btn--outline{
            background: transparent;
            color: #0f766e;
            border: 1px solid rgba(15,118,110,.35);
          }
          .fe-btn--ghost{
            background: rgba(255,255,255,.6);
            color: #0f172a;
            border: 1px solid rgba(0,0,0,.08);
          }
          .fe-input, .fe-select{
            padding: 10px 12px;
            border-radius: 12px;
            border: 1px solid rgba(0,0,0,.12);
            background: rgba(255,255,255,.85);
            outline: none;
          }
          .fe-input:focus, .fe-select:focus{
            border-color: rgba(16,185,129,.55);
            box-shadow: 0 0 0 4px rgba(16,185,129,.15);
          }
        `}</style>
      </div>
    </div>
  );
}
