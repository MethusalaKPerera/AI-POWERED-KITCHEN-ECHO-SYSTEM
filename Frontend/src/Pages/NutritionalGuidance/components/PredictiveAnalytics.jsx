import React, { useEffect, useMemo, useState } from "react";
import { getReport, getMLRisk, DEFAULT_USER_ID } from "../../../services/nutritionApi";
import "./PredictiveAnalytics.css";

function fmt(num) {
  if (num === null || num === undefined) return "-";
  const n = Number(num);
  if (!Number.isFinite(n)) return "-";
  return Math.abs(n - Math.round(n)) < 1e-9 ? String(Math.round(n)) : n.toFixed(2);
}

function labelize(key) {
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

/**
 * ✅ NEW helper:
 * Show ALL important nutrient fields that exist in the food row.
 * (This avoids "only potassium" feeling.)
 */
const IMPORTANT_NUTRIENTS = [
  "energy_kcal",
  "protein_g",
  "carbohydrate_g",
  "fat_g",
  "fiber_g",
  "sugar_g",
  "calcium_mg",
  "iron_mg",
  "zinc_mg",
  "magnesium_mg",
  "potassium_mg",
  "sodium_mg",
  "vitamin_c_mg",
  "vitamin_a_ug",
  "vitamin_d_ug",
  "vitamin_b12_ug",
  "folate_ug",
];

function getFoodNutrientPills(food) {
  if (!food) return [];

  // Take only nutrient keys that exist in the food object
  const entries = IMPORTANT_NUTRIENTS
    .filter((k) => Object.prototype.hasOwnProperty.call(food, k))
    .map((k) => [k, food[k]]);

  // Keep numeric + meaningful values
  const cleaned = entries
    .map(([k, v]) => [k, Number(v)])
    .filter(([_, v]) => Number.isFinite(v) && v > 0);

  // Sort by strongest nutrient amount (descending)
  cleaned.sort((a, b) => b[1] - a[1]);

  // Show many (but not unlimited). Increase if you want.
  const MAX_PILLS = 10;

  return cleaned.slice(0, MAX_PILLS).map(([k, v]) => ({
    key: k,
    label: labelize(k),
    value: fmt(v),
  }));
}

export default function PredictiveAnalytics({ userId = DEFAULT_USER_ID }) {
  const [period, setPeriod] = useState("monthly");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [report, setReport] = useState(null);
  const [mlRisk, setMlRisk] = useState(null);

  const loadReport = async () => {
    setLoading(true);
    setErr("");
    try {
      const [data, riskRes] = await Promise.all([
        getReport(userId, period),
        getMLRisk(userId, period),
      ]);
      setReport(data);
      setMlRisk(riskRes?.ml_deficiency_risk || null);
    } catch (e) {
      setErr(e.message || "Failed to load report");
      setReport(null);
      setMlRisk(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReport();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [period, userId]);

  const periodAvg = useMemo(() => {
    const s = report?.intake_summary;
    return s?.daily_average_over_period || s?.daily_average || {};
  }, [report]);

  const gapRows = useMemo(() => {
    if (!report?.gaps) return [];
    const gaps = report.gaps;
    const sev = report.severity || {};
    const req = report.requirements || {};

    const rows = Object.keys(gaps).map((k) => ({
      key: k,
      label: labelize(k),
      required: req[k],
      intake: periodAvg[k],
      gap: gaps[k],
      severity: sev[k] || "ok",
    }));

    rows.sort((a, b) => Number(b.gap || 0) - Number(a.gap || 0));
    return rows;
  }, [report, periodAvg]);

  const riskTone = useMemo(() => {
    const v = String(mlRisk || "").toUpperCase();
    if (v === "HIGH") return "risk-high";
    if (v === "MEDIUM") return "risk-med";
    return "risk-low";
  }, [mlRisk]);

  return (
    <div className="pa-wrap">
      {/* Hero */}
      <div className="pa-hero">
        <div>
          <h2 className="pa-title">Predictive Analytics</h2>
          <p className="pa-subtitle">
            Deficiency report based on your profile, health conditions, and intake logs.
          </p>
        </div>

        <div className="pa-meta">
          <div className="pa-pill">
            User: <b>{userId || DEFAULT_USER_ID}</b>
          </div>
        </div>
      </div>

      {/* Period controls */}
      <div className="pa-controlsRow">
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

      </div>

      {err && <div className="pa-alert pa-alert-error">{err}</div>}
      {!err && loading && <div className="pa-alert">Loading report...</div>}

      {!loading && report && (
        <>
          <div className="pa-grid">
            <div className={`pa-card pa-ml ${riskTone}`}>
              <div className="pa-card-title">ML Predicted Deficiency Risk</div>
              <div className="pa-riskValue">{mlRisk || "N/A"}</div>
              <p className="pa-subtitle2">
                Predicted using a supervised ML classifier based on intake patterns and demographic features.
              </p>
            </div>

            <div className="pa-card">
              <div className="pa-card-title">User Profile</div>
              <div className="pa-kv">
                <div>
                  <div className="k">User</div>
                  <div className="v">{report.profile?.user_id || userId}</div>
                </div>
                <div>
                  <div className="k">Age</div>
                  <div className="v">{report.profile?.age}</div>
                </div>
                <div>
                  <div className="k">Gender</div>
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
                <div>
                  <div className="k">Period days</div>
                  <div className="v">{report.intake_summary?.period_days ?? "-"}</div>
                </div>
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

          <div className="pa-card pa-table-card">
            <div className="pa-card-title">Nutrient Gaps (Daily)</div>
            <div className="pa-table-wrap">
              <table className="pa-table">
                <thead>
                  <tr>
                    <th>Nutrient</th>
                    <th>Required</th>
                    <th>Intake Avg (period)</th>
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
                      <td className={Number(r.gap) > 0 ? "gap-pos" : "gap-ok"}>{fmt(r.gap)}</td>
                      <td><SeverityBadge level={r.severity} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* ✅ UPDATED RECOMMENDED FOODS */}
          <div className="pa-card">
            <div className="pa-card-title">Recommended Foods</div>
      
            {report.recommendations?.length ? (
              <div className="rec-grid">
                {report.recommendations.map((f) => {
                  const pills = getFoodNutrientPills(f);

                  return (
                    <div className="rec-item" key={f.food_id || f.food_name}>
                      <div className="rec-name">{f.food_name}</div>

                      {pills.length ? (
                        <div className="rec-nutrients">
                          {pills.map((p) => (
                            <div className="pill" key={p.key}>
                              {p.label}: {p.value}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="muted">
                          Nutrient values not available in this recommendation row.
                        </div>
                      )}
                    </div>
                  );
                })}
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
