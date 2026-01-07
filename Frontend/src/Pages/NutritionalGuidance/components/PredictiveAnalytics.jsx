import React, { useEffect, useMemo, useState } from "react";
import {
  getReport,
  getMLRisk,
  getTrainedTwoWeekReport,
  DEFAULT_USER_ID,
} from "../../../services/nutritionApi";
import "./PredictiveAnalytics.css";

// --------------------------------------------------------
// We standardize to *_ug in the UI to prevent duplicates.
// --------------------------------------------------------
const CANONICAL_KEY = {
  vitamin_a_mcg: "vitamin_a_ug",
  vitamin_d_mcg: "vitamin_d_ug",
  vitamin_b12_mcg: "vitamin_b12_ug",
  folate_mcg: "folate_ug",
};

function canonicalKey(k) {
  return CANONICAL_KEY[k] || k;
}

function getValueByAnyKey(obj, key) {
  if (!obj) return undefined;

  if (Object.prototype.hasOwnProperty.call(obj, key)) return obj[key];

  const alias = Object.keys(CANONICAL_KEY).find((a) => CANONICAL_KEY[a] === key);
  if (alias && Object.prototype.hasOwnProperty.call(obj, alias)) return obj[alias];

  return undefined;
}

function fmt(num) {
  if (num === null || num === undefined) return "-";
  const n = Number(num);
  if (!Number.isFinite(n)) return "-";
  return Math.abs(n - Math.round(n)) < 1e-9 ? String(Math.round(n)) : n.toFixed(2);
}

function labelize(key) {
  key = canonicalKey(key);

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

function LevelChip({ level }) {
  const v = String(level || "").toUpperCase();
  const cls =
    v === "OK"
      ? "tw-chip tw-ok"
      : v === "LOW"
      ? "tw-chip tw-low"
      : v === "MODERATE"
      ? "tw-chip tw-mod"
      : "tw-chip tw-high";
  return <span className={cls}>{v || "N/A"}</span>;
}

function TwoWeekReportModal({ open, onClose, data }) {
  if (!open) return null;

  const p = data?.profile || {};
  const nutrients = data?.nutrients || [];
  const lines = data?.report_text || [];

  return (
    <div className="tw-modal" role="dialog" aria-modal="true">
      <div className="tw-modal__card">
        <div className="tw-modal__header">
          <div>
            <div className="tw-title">Next 2 Weeks Nutrient Report</div>
            <div className="tw-sub">
              Forecast window: <b>{data?.forecast_start}</b> to <b>{data?.forecast_end}</b>
            </div>
          </div>

          <button className="tw-close" onClick={onClose} type="button">
            ✕
          </button>
        </div>

        <div className="tw-section">
          <div className="tw-sectionTitle">User Profile</div>
          <div className="tw-kv">
            <div>
              <div className="k">User</div>
              <div className="v">{p.user_id || "-"}</div>
            </div>
            <div>
              <div className="k">Age</div>
              <div className="v">{p.age ?? "-"}</div>
            </div>
            <div>
              <div className="k">Gender</div>
              <div className="v">{p.group || "-"}</div>
            </div>
            <div>
              <div className="k">Conditions</div>
              <div className="v">
                {(p.conditions || []).length ? p.conditions.join(", ") : "None"}
              </div>
            </div>
          </div>
        </div>

        <div className="tw-section">
          <div className="tw-sectionTitle">Overall Risk (ML)</div>
          <div className="tw-ml">{data?.ml_overall_deficiency_risk || "N/A"}</div>
          {lines.length ? (
            <ul className="tw-lines">
              {lines.map((t, i) => (
                <li key={i}>{t}</li>
              ))}
            </ul>
          ) : null}
        </div>

        <div className="tw-section">
          <div className="tw-sectionTitle">Trained Nutrients (14-day forecast)</div>

          <div className="tw-nutrients">
            {nutrients.map((n) => (
              <div className="tw-nutrient" key={n.key}>
                <div className="tw-nutrientTop">
                  <div className="tw-nutrientName">{n.label}</div>
                  <LevelChip level={n.deficiency_level_next_14d} />
                </div>

                <div className="tw-miniGrid">
                  <div>
                    <div className="k">Required / day</div>
                    <div className="v">{fmt(n.required_per_day)}</div>
                  </div>
                  <div>
                    <div className="k">Expected intake / day</div>
                    <div className="v">{fmt(n.expected_intake_per_day)}</div>
                  </div>
                  <div>
                    <div className="k">Required (14 days)</div>
                    <div className="v">{fmt(n.required_total_14d)}</div>
                  </div>
                  <div>
                    <div className="k">Expected (14 days)</div>
                    <div className="v">{fmt(n.expected_total_14d)}</div>
                  </div>
                  <div className="tw-deficit">
                    <div className="k">Deficit (14 days)</div>
                    <div className="v">{fmt(n.deficit_total_14d)}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="tw-note">
            Note: This forecast assumes you continue the same intake pattern. If your meals improve, the
            deficiency levels will reduce.
          </div>
        </div>

        <div className="tw-footer">
          <button className="tw-btn" onClick={onClose} type="button">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * Show important nutrient pills in Recommended Foods section
 */
const IMPORTANT_NUTRIENTS = Array.from(
  new Set(
    [
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

      "vitamin_a_mcg",
      "vitamin_d_mcg",
      "vitamin_b12_mcg",
      "folate_mcg",
    ].map(canonicalKey)
  )
);

function getFoodNutrientPills(food) {
  if (!food) return [];

  const entries = IMPORTANT_NUTRIENTS
    .map((k) => [k, getValueByAnyKey(food, k)])
    .filter(([_, v]) => v !== undefined);

  const cleaned = entries
    .map(([k, v]) => [canonicalKey(k), Number(v)])
    .filter(([_, v]) => Number.isFinite(v) && v > 0);

  cleaned.sort((a, b) => b[1] - a[1]);

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

  //  two-week report
  const [twoWeekOpen, setTwoWeekOpen] = useState(false);
  const [twoWeekLoading, setTwoWeekLoading] = useState(false);
  const [twoWeekErr, setTwoWeekErr] = useState("");
  const [twoWeekData, setTwoWeekData] = useState(null);

  const loadReport = async () => {
    setLoading(true);
    setErr("");
    try {
      const [data, riskRes] = await Promise.all([getReport(userId, period), getMLRisk(userId, period)]);
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

  const openTwoWeekReport = async () => {
    setTwoWeekErr("");
    setTwoWeekLoading(true);
    setTwoWeekOpen(true);
    try {
      const data = await getTrainedTwoWeekReport(userId, period, 14);
      setTwoWeekData(data);
    } catch (e) {
      setTwoWeekErr(e.message || "Failed to load 2-week report");
      setTwoWeekData(null);
    } finally {
      setTwoWeekLoading(false);
    }
  };

  const periodAvg = useMemo(() => {
    const s = report?.intake_summary;
    return s?.daily_average_over_period || s?.daily_average || {};
  }, [report]);

  const gapRows = useMemo(() => {
    if (!report?.gaps) return [];

    const gaps = report.gaps || {};
    const sev = report.severity || {};
    const req = report.requirements || {};

    const map = new Map();

    for (const k of Object.keys(gaps)) {
      const ck = canonicalKey(k);

      const existing = map.get(ck) || {
        key: ck,
        label: labelize(ck),
        required: undefined,
        intake: undefined,
        gap: undefined,
        severity: "ok",
      };

      const requiredVal =
        getValueByAnyKey(req, ck) ?? getValueByAnyKey(req, k) ?? existing.required;

      const intakeVal =
        getValueByAnyKey(periodAvg, ck) ?? getValueByAnyKey(periodAvg, k) ?? existing.intake;

      const gapVal = gaps[ck] ?? gaps[k] ?? existing.gap;
      const sevVal = sev[ck] || sev[k] || existing.severity;

      map.set(ck, {
        ...existing,
        required: requiredVal,
        intake: intakeVal,
        gap: gapVal,
        severity: sevVal,
      });
    }

    const rows = Array.from(map.values());
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

        {/* ✅ NEW button */}
        <button className="tw-openBtn" onClick={openTwoWeekReport} type="button">
          Next 2 Weeks Report
        </button>
      </div>

      {err && <div className="pa-alert pa-alert-error">{err}</div>}
      {!err && loading && <div className="pa-alert">Loading report...</div>}

      {/* ✅ Modal */}
      <TwoWeekReportModal
        open={twoWeekOpen}
        onClose={() => setTwoWeekOpen(false)}
        data={twoWeekData}
      />
      {twoWeekOpen && twoWeekLoading && (
        <div className="tw-toast">Loading Next 2 Weeks Report...</div>
      )}
      {twoWeekOpen && twoWeekErr && <div className="tw-toast tw-toast-err">{twoWeekErr}</div>}

      {!loading && report && (
        <>
          <div className="pa-grid">
            <div className={`pa-card pa-ml ${riskTone}`}>
              <div className="pa-card-title">ML Predicted Deficiency Risk</div>
              <div className="pa-riskValue">{mlRisk || "N/A"}</div>
              <p className="pa-subtitle2">
                Predicted using a supervised Random Forest classifier trained on nutrient intake patterns and user profile data.
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
                      <td>
                        <SeverityBadge level={r.severity} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

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
