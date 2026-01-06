import React, { useEffect, useMemo, useState } from "react";
import { getIntakeSummary, DEFAULT_USER_ID } from "../../../services/nutritionApi";
import "./NutritionTracker.css";

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

function MiniBars({ title, items, unit = "" }) {
  const maxVal = useMemo(() => {
    const m = Math.max(...items.map((x) => Number(x.value || 0)));
    return m > 0 ? m : 1;
  }, [items]);

  return (
    <div className="nt-card">
      <div className="nt-card-title">{title}</div>
      <div className="nt-bars">
        {items.map((it) => {
          const v = Number(it.value || 0);
          const w = Math.max(3, Math.round((v / maxVal) * 100));
          return (
            <div className="nt-bar-row" key={it.label}>
              <div className="nt-bar-label">{it.label}</div>
              <div className="nt-bar-track">
                <div className="nt-bar-fill" style={{ width: `${w}%` }} />
              </div>
              <div className="nt-bar-value">
                {fmt(v)} {unit}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function NutritionTracker({ userId = DEFAULT_USER_ID }) {
  const [period, setPeriod] = useState("monthly");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [summary, setSummary] = useState(null);

  const load = async () => {
    setLoading(true);
    setErr("");
    try {
      const data = await getIntakeSummary(userId || DEFAULT_USER_ID, period);
      setSummary(data);
    } catch (e) {
      setErr(e.message || "Failed to load summary");
      setSummary(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [period, userId]);

  const nutrients = useMemo(() => {
    if (!summary) return [];
    const totals = summary.totals || {};
    const avg = summary.daily_average_over_period || summary.daily_average || {};
    const keys = Object.keys(totals);

    const priority = [
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

    const ordered = [
      ...priority.filter((k) => k in totals),
      ...keys.filter((k) => !priority.includes(k)),
    ];

    return ordered.map((k) => ({
      key: k,
      label: labelize(k),
      total: totals[k],
      daily: avg[k],
    }));
  }, [summary]);

  const topDaily = useMemo(() => {
    if (!summary) return [];
    const a = summary.daily_average_over_period || summary.daily_average || {};
    return [
      { label: "Energy", value: a.energy_kcal || 0 },
      { label: "Protein", value: a.protein_g || 0 },
      { label: "Carbs", value: a.carbohydrate_g || 0 },
      { label: "Fat", value: a.fat_g || 0 },
      { label: "Fiber", value: a.fiber_g || 0 },
    ];
  }, [summary]);

  return (
    <div className="nt-wrap">
      {/* ✅ HERO (same style as MealLogger, no SmartKitchen text) */}
      <div className="nt-hero">
        <div>
          <h2 className="nt-title">Nutrition Tracker</h2>
          <p className="nt-subtitle">
            Weekly / Last-30-days totals and daily averages (based on full period days).
          </p>
        </div>

        <div className="nt-meta">
          <div className="nt-pill">
            User: <b>{userId || DEFAULT_USER_ID}</b>
          </div>
        </div>
      </div>

      {/* Period toggle (no refresh button) */}
      <div className="nt-controls">
        <div className="seg">
          <button
            className={period === "weekly" ? "seg-btn active" : "seg-btn"}
            onClick={() => setPeriod("weekly")}
            type="button"
            disabled={loading}
          >
            Weekly
          </button>
          <button
            className={period === "monthly" ? "seg-btn active" : "seg-btn"}
            onClick={() => setPeriod("monthly")}
            type="button"
            disabled={loading}
          >
            Last 30 Days
          </button>
        </div>
      </div>

      {err && <div className="nt-alert nt-alert-error">{err}</div>}
      {!err && loading && <div className="nt-alert">Loading summary...</div>}

      {!loading && summary && (
        <>
          <div className="nt-grid">
            <div className="nt-card">
              <div className="nt-card-title">Period Summary</div>
              <div className="nt-kv">
                <div>
                  <div className="k">Period</div>
                  <div className="v">{summary.period}</div>
                </div>
                <div>
                  <div className="k">Start</div>
                  <div className="v">{summary.date_start}</div>
                </div>
                <div>
                  <div className="k">End</div>
                  <div className="v">{summary.date_end}</div>
                </div>
                <div>
                  <div className="k">Period days</div>
                  <div className="v">{summary.period_days}</div>
                </div>
              </div>
            </div>

            <div className="nt-card">
              <div className="nt-card-title">Logging</div>
              <div className="nt-kv">
                <div>
                  <div className="k">Days logged (this view)</div>
                  <div className="v">{summary.days_logged}</div>
                </div>
                <div>
                  <div className="k">Days logged (last 30 days)</div>
                  <div className="v">{summary.days_logged_last30 ?? "-"}</div>
                </div>
                <div>
                  <div className="k">Logs used</div>
                  <div className="v">{summary.logs_used}</div>
                </div>
                <div>
                  <div className="k">User</div>
                  <div className="v">{summary.user_id}</div>
                </div>
              </div>

              <div className="nt-note">
                Averages are calculated across the full period ({summary.period_days} days).
              </div>
            </div>

            <MiniBars title="Daily Averages (Period-based)" items={topDaily} />
          </div>

          <div className="nt-card nt-table-card">
            <div className="nt-card-title">Totals vs Daily Average (Period-based)</div>
            <div className="nt-table-wrap">
              <table className="nt-table">
                <thead>
                  <tr>
                    <th>Nutrient</th>
                    <th>Total (period)</th>
                    <th>Daily Average</th>
                  </tr>
                </thead>
                <tbody>
                  {nutrients.map((n) => (
                    <tr key={n.key}>
                      <td>{n.label}</td>
                      <td>{fmt(n.total)}</td>
                      <td>{fmt(n.daily)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
