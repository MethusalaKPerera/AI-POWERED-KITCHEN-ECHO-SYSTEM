import React, { useEffect, useMemo, useState } from "react";
import "./DashboardHomeNG.css";

// correct path based on your project structure
import { getIntakeSummary } from "../../../services/nutritionApi";

const DashboardHome = ({ userName = "demo", periodLabel = "This Month" }) => {
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    let alive = true;

    async function load() {
      setLoading(true);
      setErr("");
      try {
        const s = await getIntakeSummary(userName, "monthly");
        if (!alive) return;
        setSummary(s || null);
      } catch (e) {
        if (!alive) return;
        setErr(e.message || "Failed to load dashboard summary");
      } finally {
        if (alive) setLoading(false);
      }
    }

    load();
    return () => {
      alive = false;
    };
  }, [userName]);

  // Stats (still placeholders - you can connect later)
  const stats = [
    {
      title: "Nutrition Status",
      value: "Good",
      sub: periodLabel,
      icon: "🥗",
      tone: "good",
    },
    { title: "Avg Calories", value: "2,150", sub: "kcal/day", icon: "⚡", tone: "info" },

    // ✅ UPDATED HERE
    {
      title: "Deficiency Risk",
      value: "HIGH",
      sub: "ML prediction",
      icon: "🧠",
      tone: "danger",
    },

    { title: "Logged Days", value: "30", sub: "tracked days", icon: "📅", tone: "neutral" },
  ];

  // ✅ Only names (top_foods from backend)
  const topFoodNames = useMemo(() => {
    if (!Array.isArray(summary?.top_foods)) return [];
    return summary.top_foods
      .map((x) => (x?.food_name || x?.name || "").trim())
      .filter(Boolean)
      .slice(0, 3);
  }, [summary]);

  return (
    <div className="ngdash">
      {/* Hero */}
      <div className="ngdash-hero">
        <div className="ngdash-hero-left">
          <div className="ngdash-hero-badge">SmartKitchen • Nutrition Guidance</div>

          <h1 className="ngdash-title">
            Welcome, <span className="ngdash-name">{userName}</span>
          </h1>

          <p className="ngdash-subtitle">
            Track meals, analyze intake, and get AI-powered deficiency insights to support healthier decisions.
          </p>

          <p className="ngdash-note">
            This module generates personalized nutrition reports using your profile, intake history, and predictive ML
            risk scoring.
          </p>
        </div>

        <div className="ngdash-hero-right">
          <div className="ngdash-orb">🧬</div>
          <div className="ngdash-orb-sub">Personalized Nutrition Intelligence</div>
        </div>
      </div>

      {/* Stats */}
      <div className="ngdash-stats">
        {stats.map((s) => (
          <div key={s.title} className={`ngdash-stat ng-${s.tone}`}>
            <div className="ngdash-stat-icon">{s.icon}</div>
            <div className="ngdash-stat-info">
              <div className="ngdash-stat-title">{s.title}</div>
              <div className="ngdash-stat-value">{s.value}</div>
              <div className="ngdash-stat-sub">{s.sub}</div>
            </div>
          </div>
        ))}
      </div>

      {/* ✅ Top 3 foods (ONLY NAMES) */}
      <div className="ngdash-topfoods">
        <div className="ngdash-panel">
          <div className="ngdash-panel-head">
            <h3>🍛 Top 3 Eating Items</h3>
            <p>Most frequently logged foods in your eating pattern.</p>
          </div>

          {loading && <div className="ngdash-muted">Loading top foods...</div>}
          {err && <div className="ngdash-error">{err}</div>}

          {!loading && !err && topFoodNames.length === 0 && (
            <div className="ngdash-empty">No foods detected for this period. (Check user_id or date range.)</div>
          )}

          {!loading && !err && topFoodNames.length > 0 && (
            <div className="ngdash-list">
              {topFoodNames.map((name, idx) => (
                <div className="ngdash-list-item" key={`${name}-${idx}`}>
                  <div className="ngdash-rank">{idx + 1}</div>
                  <div className="ngdash-list-main">
                    <div className="ngdash-list-title">{name}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Feature cards */}
      <div className="ngdash-features">
        <div className="ngdash-card">
          <h3>📄 Deficiency Report</h3>
          <p>
            Compare your intake against age-based nutrient requirements and highlight deficiencies with clear
            recommendations.
          </p>
          <ul>
            <li>✓ Requirements by age</li>
            <li>✓ Condition-aware adjustments</li>
            <li>✓ Priority nutrient gaps</li>
          </ul>
        </div>

        <div className="ngdash-card">
          <h3>🧠 ML Risk Classification</h3>
          <p>
            A supervised ML model predicts deficiency risk levels (LOW/MEDIUM/HIGH) to support early intervention.
          </p>
          <ul>
            <li>✓ Risk stratification</li>
            <li>✓ Pattern-based learning</li>
            <li>✓ Interpretable output</li>
          </ul>
        </div>

        <div className="ngdash-card">
          <h3>🍽️ Meal Logging</h3>
          <p>Log your meals quickly using food search and serving quantities. Better logs give better insights.</p>
          <ul>
            <li>✓ Food search</li>
            <li>✓ Serving-based quantity</li>
            <li>✓ Daily tracking</li>
          </ul>
        </div>

        <div className="ngdash-card">
          <h3>👤 User Profile</h3>
          <p>Personalize your analysis with name, gender, age and health conditions for accurate targets.</p>
          <ul>
            <li>✓ Age & gender</li>
            <li>✓ Condition selection</li>
            <li>✓ Personalized targets</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default DashboardHome;
