import React, { useEffect, useMemo, useState } from "react";
import {
  getReport,
  getMLRisk,
  getTrainedTwoWeekReport,
  simulateMLRisk,
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

// Keys we don't want shown in the UI
const EXCLUDE_KEYS = new Set([
  "vitamin_a_ug",
  "vitamin_d_ug",
  "vitamin_b12_ug",
  "folate_ug",
  "vitamin_a_mcg",
  "vitamin_d_mcg",
  "vitamin_b12_mcg",
  "folate_mcg",
  "added_sugar_g_upper",
  "sodium_mg_upper",
]);

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

function getRecommendations(risk) {
  if (!risk || typeof risk === "string") return [];
  return risk.recommendations || [];
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
            <div className="tw-title">Future Forecast Report</div>
            <div className="tw-sub">
              Forecasting window: <b>{data?.forecast_start}</b> to <b>{data?.forecast_end}</b>
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
          <div className="tw-sectionTitle">14-Day Trajectory projection</div>
          <p className="tw-explanation">
            Based on your past logged intake data, here is the mathematically projected outcome over the next 14 days if you continue this behavior.
          </p>

          <div className="tw-nutrients">
            {nutrients
              .filter((n) => !EXCLUDE_KEYS.has(n.key))
              .map((n) => (
                <div className="tw-nutrient-card" key={n.key}>
                  <div className="tw-nutrientTop">
                    <div className="tw-nutrientName">{n.label}</div>
                    <LevelChip level={n.deficiency_level_next_14d} />
                  </div>

                  <div className="forecast-comparison">
                    <div className="forecast-past">
                      <div className="forecast-label">Past Daily Avg</div>
                      <div className="forecast-value">{fmt(n.expected_intake_per_day)}</div>
                    </div>
                    <div className="forecast-future">
                      <div className="forecast-label">14-Day Projection</div>
                      <div className="forecast-value">{fmt(n.expected_total_14d)}</div>
                    </div>
                    <div className="forecast-target">
                      <div className="forecast-label">14-Day Goal</div>
                      <div className="forecast-value">{fmt(n.required_total_14d)}</div>
                    </div>
                    <div className={`forecast-gap ${Number(n.deficit_total_14d) > 0 ? 'gap-alert' : 'gap-ok'}`}>
                      <div className="forecast-label">Expected Deficit</div>
                      <div className="forecast-value">{fmt(n.deficit_total_14d)}</div>
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
            Close Forecast
          </button>
        </div>
      </div>
    </div>
  );
}

function getRiskLevel(risk) {
  if (!risk) return "";
  if (typeof risk === "string") return risk;
  return risk.risk_level || "";
}

function getRiskConfidence(risk) {
  if (!risk || typeof risk === "string" || !risk.confidence_scores) return null;

  const values = Object.values(risk.confidence_scores).map(Number);
  const max = Math.max(...values);

  return Number.isFinite(max) ? max : null;
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
    ]
      .map(canonicalKey)
      .filter((k) => !EXCLUDE_KEYS.has(k))
  )
);

function getFoodNutrientPills(food) {
  if (!food) return [];

  const entries = IMPORTANT_NUTRIENTS
    .map((k) => [k, getValueByAnyKey(food, k)])
    .filter(([k, v]) => v !== undefined && !EXCLUDE_KEYS.has(k));

  const cleaned = entries
    .map(([k, v]) => [canonicalKey(k), Number(v)])
    .filter(([k, v]) => !EXCLUDE_KEYS.has(k) && Number.isFinite(v) && v > 0);

  cleaned.sort((a, b) => b[1] - a[1]);

  const MAX_PILLS = 10;
  return cleaned.slice(0, MAX_PILLS).map(([k, v]) => ({
    key: k,
    label: labelize(k),
    value: fmt(v),
  }));
}

function getNutrientBreakdown(risk) {
  if (!risk || typeof risk === "string") return {};
  return risk.nutrient_breakdown || {};
}

function getRiskExplanation(risk) {
  if (!risk || typeof risk === "string") return "";
  return risk.explanation || "";
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

  // Simulation Mode State
  const [simulationMode, setSimulationMode] = useState(false);
  const [simForm, setSimForm] = useState({
    age: 30,
    condition: "",
    energy_kcal: 2000,
    protein_g: 50,
    calcium_mg: 1000,
    iron_mg: 18
  });
  const [simRisk, setSimRisk] = useState(null);
  const [simLoading, setSimLoading] = useState(false);

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

  const handleSimulate = async () => {
    setSimLoading(true);
    try {
      const res = await simulateMLRisk({
        age: simForm.age,
        condition: simForm.condition || null,
        energy_kcal: simForm.energy_kcal,
        protein_g: simForm.protein_g,
        calcium_mg: simForm.calcium_mg,
        iron_mg: simForm.iron_mg
      });
      setSimRisk(res.ml_deficiency_risk);
    } catch (e) {
      alert('Failed to simulate risk: ' + e.message);
    } finally {
      setSimLoading(false);
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
      if (EXCLUDE_KEYS.has(ck)) continue;

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

    // Ensure priority keys (e.g., sugar_g) appear even if backend didn't include them
    const PRIORITY_GAP_KEYS = ["sugar_g"];
    for (const k of PRIORITY_GAP_KEYS) {
      const ck = canonicalKey(k);
      if (EXCLUDE_KEYS.has(ck) || map.has(ck)) continue;
      let requiredVal = getValueByAnyKey(req, ck) ?? getValueByAnyKey(req, k);
      const intakeVal = getValueByAnyKey(periodAvg, ck) ?? getValueByAnyKey(periodAvg, k);
      // if requirement missing but we know intake, fall back to intake so the column isn't blank
      if (requiredVal === undefined && intakeVal !== undefined) {
        requiredVal = intakeVal;
      }
      if (requiredVal === undefined && intakeVal === undefined) continue;
      const gapVal = requiredVal !== undefined && intakeVal !== undefined ? (Number(requiredVal) - Number(intakeVal)) : undefined;
      const sevVal = gapVal === undefined ? "ok" : (Number(gapVal) > 0 ? "high" : "ok");
      map.set(ck, {
        key: ck,
        label: labelize(ck),
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

  const activeRisk = simulationMode ? simRisk : mlRisk;
  const activeRiskLevel = getRiskLevel(activeRisk);
  const activeConfidence = getRiskConfidence(activeRisk);
  const activeBreakdown = getNutrientBreakdown(activeRisk);
  const activeExplanation = getRiskExplanation(activeRisk);
  const activeRecommendations = getRecommendations(activeRisk);

  const riskTone = useMemo(() => {
    const v = String(activeRiskLevel || "").toUpperCase();

    if (v === "HIGH") return "risk-high";
    if (v === "MEDIUM") return "risk-med";
    if (v === "LOW") return "risk-low";

    return "";
  }, [activeRiskLevel]);

  return (
    <div className="pa-wrap">
      <div className="pa-hero">
        <div>
          <h2 className="pa-title">Predictive Analytics</h2>
          <p className="pa-subtitle">
            Deficiency report based on your profile, health conditions, and intake logs.
          </p>
        </div>

        <div className="pa-meta" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <div className="pa-pill">
            User: <b>{userId || DEFAULT_USER_ID}</b>
          </div>
          <button
            className={`tw-openBtn ${simulationMode ? 'active' : ''}`}
            style={{ backgroundColor: simulationMode ? '#9333ea' : undefined }}
            onClick={() => setSimulationMode(!simulationMode)}
          >
            {simulationMode ? "Exit Simulation" : "Simulate ML Risk"}
          </button>
        </div>
      </div>

      <div className="pa-controlsRow">
        <div className="seg">
          <button
            className={period === "weekly" ? "seg-btn active" : "seg-btn"}
            onClick={() => setPeriod("weekly")}
            type="button"
            disabled={simulationMode}
          >
            Weekly
          </button>
          <button
            className={period === "monthly" ? "seg-btn active" : "seg-btn"}
            onClick={() => setPeriod("monthly")}
            type="button"
            disabled={simulationMode}
          >
            Monthly
          </button>
        </div>

        {/* ✅ NEW button */}
        <button className="tw-openBtn" onClick={openTwoWeekReport} type="button" disabled={simulationMode}>
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

      {/* SIMULATION FORM */}
      {simulationMode && (
        <div className="pa-card sim-card" style={{ border: '2px solid #9333ea', backgroundColor: '#faf5ff' }}>
          <div className="pa-card-title" style={{ color: '#7e22ce' }}>Simulation Mode Settings</div>
          <p className="pa-subtitle2" style={{ marginBottom: '15px' }}>Enter custom daily values to see how the model categorizes your risk.</p>

          <div className="sim-form-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '15px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 'bold', marginBottom: '5px' }}>Age</label>
              <input type="number"
                value={simForm.age}
                onChange={e => setSimForm({ ...simForm, age: e.target.value })}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 'bold', marginBottom: '5px' }}>Condition (optional)</label>
              <select value={simForm.condition}
                onChange={e => setSimForm({ ...simForm, condition: e.target.value })}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}>
                <option value="">None</option>
                <option value="Pregnancy">Pregnancy</option>
                <option value="Lactation">Lactation</option>
                <option value="Diabetes">Diabetes</option>
                <option value="Hypertension">Hypertension</option>
                <option value="Anemia">Anemia</option>
                <option value="Osteoporosis">Osteoporosis</option>
                <option value="Athletic">Athletic</option>
                <option value="Vegan">Vegan</option>
              </select>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 'bold', marginBottom: '5px' }}>Energy (kcal / day)</label>
              <input type="number"
                value={simForm.energy_kcal}
                onChange={e => setSimForm({ ...simForm, energy_kcal: e.target.value })}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 'bold', marginBottom: '5px' }}>Protein (g / day)</label>
              <input type="number"
                value={simForm.protein_g}
                onChange={e => setSimForm({ ...simForm, protein_g: e.target.value })}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 'bold', marginBottom: '5px' }}>Calcium (mg / day)</label>
              <input type="number"
                value={simForm.calcium_mg}
                onChange={e => setSimForm({ ...simForm, calcium_mg: e.target.value })}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 'bold', marginBottom: '5px' }}>Iron (mg / day)</label>
              <input type="number"
                value={simForm.iron_mg}
                onChange={e => setSimForm({ ...simForm, iron_mg: e.target.value })}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
              />
            </div>
          </div>
          <button
            onClick={handleSimulate}
            disabled={simLoading}
            style={{ padding: '10px 20px', backgroundColor: '#9333ea', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
            {simLoading ? "Calculating Risk..." : "Predict Model Risk"}
          </button>
        </div>
      )}

      {/* ML CARD and Condition Notes side by side */}
      {(!loading && report) || simulationMode ? (
        <div className={simulationMode ? "" : "pa-grid"}>
          <div className={`pa-card pa-ml ${riskTone}`}>
            <div className="pa-card-title">
              ML Predicted Deficiency Risk
              {simulationMode && (
                <span style={{
                  fontSize: '12px',
                  marginLeft: '10px',
                  backgroundColor: 'rgba(255,255,255,0.4)',
                  padding: '2px 6px',
                  borderRadius: '4px'
                }}>
                  (Simulated)
                </span>
              )}
            </div>

            <div className="pa-riskValue">{activeRiskLevel || "N/A"}</div>

            {activeConfidence !== null && (
              <div className="pa-subtitle2">
                Confidence: {(activeConfidence * 100).toFixed(1)}%
              </div>
            )}

            {/* 🔥 NEW: Explanation */}
            {activeExplanation && (
              <div className="pa-note">
                {activeExplanation}
              </div>
            )}

            {/* 🔥 NEW: Nutrient ML Breakdown */}
            <div style={{ marginTop: "12px", display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "10px" }}>
              {Object.entries(activeBreakdown).map(([nutrient, data]) => (
                <div key={nutrient} style={{
                  padding: "10px",
                  borderRadius: "12px",
                  background: "rgba(255,255,255,0.7)",
                  border: "1px solid rgba(148,163,184,0.3)"
                }}>
                  <div style={{ fontWeight: "900", fontSize: "13px" }}>
                    {nutrient.toUpperCase()}
                  </div>

                  <div style={{
                    fontSize: "14px",
                    fontWeight: "1000",
                    color:
                      data.risk_level === "HIGH"
                        ? "#dc2626"
                        : data.risk_level === "MEDIUM"
                          ? "#f59e0b"
                          : "#16a34a"
                  }}>
                    {data.risk_level}
                  </div>

                  <div style={{ fontSize: "11px", color: "#475569" }}>
                    Ratio: {data.ratio_used}
                  </div>

                  {data.confidence && (
                    <div style={{ fontSize: "11px", color: "#475569" }}>
                      {(data.confidence * 100).toFixed(1)}%
                    </div>
                  )}
                </div>
              ))}
            </div>

          </div>
          {!simulationMode && (
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
          )}
        </div>
      ) : null
      }

      {
        !loading && report && !simulationMode && (
          <>
            <div className="pa-grid">
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

              {activeRecommendations.length > 0 && (
                <div style={{ marginTop: "16px" }}>
                  <div style={{ fontWeight: "900", marginBottom: "8px" }}>
                    Recommended Actions
                  </div>

                  {activeRecommendations.map((rec, i) => (
                    <div key={i} style={{
                      padding: "10px",
                      marginBottom: "8px",
                      borderRadius: "10px",
                      background:
                        rec.priority === "HIGH"
                          ? "#fee2e2"
                          : "#fef3c7",
                      color:
                        rec.priority === "HIGH"
                          ? "#991b1b"
                          : "#92400e"
                    }}>
                      <b>{rec.nutrient.toUpperCase()}</b>: {rec.advice}
                    </div>
                  ))}
                </div>
              )}
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
        )
      }
    </div >
  );
}
