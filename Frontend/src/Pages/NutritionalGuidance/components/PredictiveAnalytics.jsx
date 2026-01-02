import React, { useEffect, useMemo, useState } from "react";
import { getReport } from "../../../services/nutritionApi";
import "./PredictiveAnalytics.css";

function fmt(num) {
  if (num === null || num === undefined) return "-";
  const n = Number(num);
  if (!Number.isFinite(n)) return "-";
  // show integers without decimals, else 2 decimals
  return Math.abs(n - Math.round(n)) < 1e-9 ? String(Math.round(n)) : n.toFixed(2);
}

function labelize(key) {
  // energy_kcal -> Energy (kcal)
  const map = {
    energy_kcal: "Energy (kcal)",
    protein_g: "Protein (g)",
    fat_g: "Fat (g)",
    carbohydrate_g: "Carbohydrate (g)",
    fiber_g: "Fiber (g)",
    sugar_g: "Sugar (g)",
    calcium_mg: "Calcium (mg)",
    iron_mg: "Iron (mg)",
    zinc_mg: "Zinc (mg)",
    magnesium_mg: "Magnesium (mg)",
    potassium_mg: "Potassium (mg)",
    sodium_mg: "Sodium (mg)",
    vitamin_c_mg: "Vitamin C (mg)",
    vitamin_a_ug: "Vitamin A (µg)",
    vitamin_d_ug: "Vitamin D (µg)",
    vitamin_b12_ug: "Vitamin B12 (µg)",
    folate_ug: "Folate (µg)",
  };
  return map[key] || key;
}

function SeverityBadge({ level }) {
  const cls =
    level === "ok"
      ? "sev sev-ok"
      : level === "low"
      ? "sev sev-low"
      : level === "moderate"
      ? "sev sev-mod"
      : "sev sev-high";

  const text =
    level === "ok"
      ? "OK"
      : level === "low"
      ? "Low gap"
      : level === "moderate"
      ? "Moderate"
      : "High";

  return <span className={cls}>{text}</span>;
}

export default function PredictiveAnalytics({ userId = "demo" }) {
  const [period, setPeriod] = useState("monthly"); // weekly | monthly
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [report, setReport] = useState(null);

  const loadReport = async () => {
    setLoading(true);
    setErr("");
    try {
      const data = await getReport(userId, period);
      setReport(data);
    } catch (e) {
      setErr(e.message || "Failed to load report");
      setReport(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReport();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [period, userId]);

  const gapRows = useMemo(() => {
    if (!report?.gaps) return [];
    const gaps = report.gaps;
    const sev = report.severity || {};
    const req = report.requirements || {};
    const avg = report.intake_summary?.daily_average || {};

    const rows = Object.keys(gaps).map((k) => ({
      key: k,
      label: labelize(k),
      required: req[k],
      intake: avg[k],
      gap: gaps[k],
      severity: sev[k] || "ok",
    }));

    // show biggest missing first (positive gap high -> top)
    rows.sort((a, b) => Number(b.gap || 0) - Number(a.gap || 0));
    return rows;
  }, [report]);

  return (
    <div className="pa-wrap">
      <div className="pa-head">
        <div>
          <h2 className="pa-title">Predictive Analytics</h2>
          <p className="pa-subtitle">
            Deficiency report based on your age group, health conditions, and intake logs.
          </p>
        </div>

        <div className="pa-controls">
          <div className="seg">
            <button
              className={period === "weekly" ? "seg-btn active" : "seg-btn"}
              onClick={() => setPeriod("weekly")}
              type="button"
            >
              Weekly
            </button>
            <button
              className={period === "monthly" ? "seg-btn active" : "seg-btn"}
              onClick={() => setPeriod("monthly")}
              type="button"
            >
              Monthly
            </button>
          </div>

          <button className="refresh-btn" onClick={loadReport} type="button" disabled={loading}>
            {loading ? "Loading..." : "Refresh"}
          </button>
        </div>
      </div>

      {err && <div className="pa-alert pa-alert-error">{err}</div>}

      {!err && loading && <div className="pa-alert">Loading report...</div>}

      {!loading && report && (
        <>
          {/* Top summary cards */}
          <div className="pa-grid">
            <div className="pa-card">
              <div className="pa-card-title">User Profile</div>
              <div className="pa-kv">
                <div>
                  <div className="k">User ID</div>
                  <div className="v">{report.profile?.user_id || userId}</div>
                </div>
                <div>
                  <div className="k">Age</div>
                  <div className="v">{report.profile?.age}</div>
                </div>
                <div>
                  <div className="k">Group</div>
                  <div className="v">{report.profile?.group}</div>
                </div>
                <div>
                  <div className="k">Conditions</div>
                  <div className="v">
                    {(report.profile?.conditions || []).length
                      ? report.profile.conditions.join(", ")
                      : "None"}
                  </div>
                </div>
              </div>
            </div>

            <div className="pa-card">
              <div className="pa-card-title">Log Coverage</div>
              <div className="pa-kv">
                <div>
                  <div className="k">Period</div>
                  <div className="v">{report.period}</div>
                </div>
                <div>
                  <div className="k">Start</div>
                  <div className="v">{report.intake_summary?.date_start}</div>
                </div>
                <div>
                  <div className="k">End</div>
                  <div className="v">{report.intake_summary?.date_end}</div>
                </div>
                <div>
                  <div className="k">Days logged</div>
                  <div className="v">{report.intake_summary?.days_logged}</div>
                </div>
                <div>
                  <div className="k">Logs used</div>
                  <div className="v">{report.intake_summary?.logs_used}</div>
                </div>
              </div>
              <div className="pa-note">
                Tip: If “days logged” is low, gaps will look very high. Log meals for multiple days
                for realistic monthly results.
              </div>
            </div>

            <div className="pa-card">
              <div className="pa-card-title">Condition Notes</div>
              {report.condition_notes?.length ? (
                <ul className="pa-notes">
                  {report.condition_notes.slice(0, 6).map((n, idx) => (
                    <li key={idx}>
                      <b>{n.condition}</b>: {n.note}{" "}
                      {n.nutrient ? <span className="muted">({n.nutrient})</span> : null}
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="muted">No condition-specific notes.</div>
              )}
            </div>
          </div>

          {/* Gap table */}
          <div className="pa-card pa-table-card">
            <div className="pa-card-title">Nutrient Gaps (Daily)</div>
            <div className="pa-table-wrap">
              <table className="pa-table">
                <thead>
                  <tr>
                    <th>Nutrient</th>
                    <th>Required</th>
                    <th>Intake Avg</th>
                    <th>Gap</th>
                    <th>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {gapRows.map((r) => (
                    <tr key={r.key}>
                      <td className="nut">{r.label}</td>
                      <td>{fmt(r.required)}</td>
                      <td>{fmt(r.intake)}</td>
                      <td className={Number(r.gap) > 0 ? "gap-pos" : "gap-ok"}>
                        {fmt(r.gap)}
                      </td>
                      <td>
                        <SeverityBadge level={r.severity} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recommendations */}
          <div className="pa-card">
            <div className="pa-card-title">Recommended Foods</div>
            <p className="pa-subtitle2">
              Foods selected from your dataset to support the top missing nutrients.
            </p>

            {report.recommendations?.length ? (
              <div className="rec-grid">
                {report.recommendations.map((f) => (
                  <div className="rec-item" key={f.food_id || f.food_name}>
                    <div className="rec-name">{f.food_name}</div>
                    <div className="rec-meta">
                      {f.food_id ? <span>ID: {f.food_id}</span> : null}
                      {f.serving_basis ? <span>• {f.serving_basis}</span> : null}
                      {f.serving_size_g ? <span>• {f.serving_size_g}g</span> : null}
                    </div>

                    {/* show up to 3 nutrient columns that exist in response */}
                    <div className="rec-nutrients">
                      {Object.entries(f)
                        .filter(([k]) =>
                          [
                            "protein_g",
                            "fiber_g",
                            "calcium_mg",
                            "iron_mg",
                            "zinc_mg",
                            "magnesium_mg",
                            "potassium_mg",
                            "vitamin_c_mg",
                            "vitamin_a_ug",
                            "vitamin_d_ug",
                            "vitamin_b12_ug",
                            "folate_ug",
                          ].includes(k)
                        )
                        .slice(0, 3)
                        .map(([k, v]) => (
                          <div className="pill" key={k}>
                            {labelize(k)}: {fmt(v)}
                          </div>
                        ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="muted">No recommendations available yet.</div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
