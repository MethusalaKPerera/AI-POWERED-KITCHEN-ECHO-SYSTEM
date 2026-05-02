import React, { useEffect, useMemo, useState } from "react";
import "./DashboardHomeNG.css";

import {
  getIntakeSummary,
  getMLRisk,
} from "../../../services/nutritionApi";

function fmtNumber(value, digits = 0) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "-";
  return n.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function getRiskLevel(risk) {
  if (!risk) return "N/A";
  if (typeof risk === "string") return risk;
  return risk.risk_level || "N/A";
}

function getRiskConfidence(risk) {
  if (!risk || typeof risk === "string") return null;

  if (risk.confidence !== undefined && risk.confidence !== null) {
    return Number(risk.confidence);
  }

  if (risk.confidence_scores) {
    const values = Object.values(risk.confidence_scores).map(Number);
    const max = Math.max(...values);
    return Number.isFinite(max) ? max : null;
  }

  return null;
}

function getMainCauses(risk) {
  if (!risk || typeof risk === "string") return [];

  if (Array.isArray(risk.main_causes)) {
    return risk.main_causes;
  }

  if (risk.nutrient_breakdown) {
    return Object.entries(risk.nutrient_breakdown)
      .filter(([, data]) => String(data?.risk_level || "").toUpperCase() === "HIGH")
      .map(([nutrient]) => nutrient);
  }

  return [];
}

function getDashboardTone(riskLevel) {
  const v = String(riskLevel || "").toUpperCase();

  if (v === "HIGH") return "danger";
  if (v === "MEDIUM") return "warn";
  if (v === "LOW") return "good";

  return "neutral";
}

function getOverallInsight(riskLevel) {
  const v = String(riskLevel || "").toUpperCase();

  if (v === "HIGH") return "Needs Attention";
  if (v === "MEDIUM") return "Moderate Risk";
  if (v === "LOW") return "Healthy Pattern";

  return "Pending";
}

const DashboardHome = ({ userName = "demo", periodLabel = "This Month" }) => {
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [summary, setSummary] = useState(null);
  const [mlRisk, setMlRisk] = useState(null);

  useEffect(() => {
    let alive = true;

    async function load() {
      setLoading(true);
      setErr("");

      try {
        const [summaryRes, riskRes] = await Promise.all([
          getIntakeSummary(userName, "monthly"),
          getMLRisk(userName, "monthly"),
        ]);

        if (!alive) return;

        setSummary(summaryRes || null);
        setMlRisk(riskRes?.ml_deficiency_risk || null);
      } catch (e) {
        if (!alive) return;
        setErr(e.message || "Failed to load dashboard summary");
        setSummary(null);
        setMlRisk(null);
      } finally {
        if (alive) setLoading(false);
      }
    }

    load();

    return () => {
      alive = false;
    };
  }, [userName]);

  const dailyAverage = useMemo(() => {
    return (
      summary?.daily_average_over_period ||
      summary?.daily_average ||
      summary?.daily_average_logged_days ||
      {}
    );
  }, [summary]);

  const avgCalories = dailyAverage?.energy_kcal ?? dailyAverage?.calories ?? null;

  const loggedDays =
    summary?.days_logged ??
    summary?.logged_days ??
    summary?.period_days ??
    "-";

  const riskLevel = getRiskLevel(mlRisk);
  const riskConfidence = getRiskConfidence(mlRisk);
  const mainCauses = getMainCauses(mlRisk);
  const riskTone = getDashboardTone(riskLevel);
  const overallInsight = getOverallInsight(riskLevel);

  const mainCauseText = mainCauses.length
    ? mainCauses.map((x) => x.charAt(0).toUpperCase() + x.slice(1)).join(", ")
    : "No major issue";

  const stats = [
    {
      title: "Overall Health Insight",
      value: overallInsight,
      sub:
        riskConfidence !== null
          ? `ML confidence ${(riskConfidence * 100).toFixed(1)}%`
          : periodLabel,
      icon: "🧬",
      tone: riskTone,
    },
    {
      title: "Avg Calories",
      value: fmtNumber(avgCalories),
      sub: "kcal/day",
      icon: "⚡",
      tone: "info",
    },
    {
      title: "Deficiency Risk",
      value: riskLevel,
      sub: `Main issue: ${mainCauseText}`,
      icon: "🧠",
      tone: riskTone,
    },
    {
      title: "Logged Days",
      value: fmtNumber(loggedDays),
      sub: "tracked days",
      icon: "📅",
      tone: "neutral",
    },
  ];

  const topFoodNames = useMemo(() => {
    if (!Array.isArray(summary?.top_foods)) return [];

    return summary.top_foods
      .map((x) => (x?.food_name || x?.name || "").trim())
      .filter(Boolean)
      .slice(0, 3);
  }, [summary]);

  return (
    <div className="ngdash">
      <div className="ngdash-hero">
        <div className="ngdash-hero-left">
          <div className="ngdash-hero-badge">
            SmartKitchen • Nutrition Guidance
          </div>

          <h1 className="ngdash-title">
            Welcome, <span className="ngdash-name">{userName}</span>
          </h1>

          <p className="ngdash-subtitle">
            Track meals, analyze intake, and get AI-powered deficiency insights
            to support healthier decisions.
          </p>

          <p className="ngdash-note">
            This module generates personalized nutrition reports using your
            profile, intake history, and predictive ML risk scoring.
          </p>
        </div>

        <div className="ngdash-hero-right">
          <div className="ngdash-orb">🧬</div>
          <div className="ngdash-orb-sub">
            Personalized Nutrition Intelligence
          </div>
        </div>
      </div>

      {err && <div className="ngdash-error">{err}</div>}
      {loading && <div className="ngdash-muted">Loading dashboard...</div>}

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

      <div className="ngdash-topfoods">
        <div className="ngdash-panel">
          <div className="ngdash-panel-head">
            <h3>🍛 Top 3 Eating Items</h3>
            <p>Most frequently logged foods in your eating pattern.</p>
          </div>

          {!loading && !err && topFoodNames.length === 0 && (
            <div className="ngdash-empty">
              No foods detected for this period. Check user ID or date range.
            </div>
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

      <div className="ngdash-features">
        <div className="ngdash-card">
          <h3>📄 Deficiency Report</h3>
          <p>
            Compare your intake against age-based nutrient requirements and
            highlight deficiencies with clear recommendations.
          </p>
          <ul>
            <li>✓ Requirements by age</li>
            <li>✓ Condition-aware adjustments</li>
            <li>✓ Priority nutrient gaps</li>
          </ul>
        </div>

        <div className="ngdash-card">
          <h3>🧠 Multi-Model ML Risk Classification</h3>
          <p>
            The system predicts overall deficiency risk and nutrient-specific
            risks using trained machine learning models.
          </p>
          <ul>
            <li>✓ Overall ML risk prediction</li>
            <li>✓ Energy, protein, calcium and iron risk models</li>
            <li>✓ Confidence-based output</li>
          </ul>
        </div>

        <div className="ngdash-card">
          <h3>🍽️ Meal Logging</h3>
          <p>
            Log your meals quickly using food search and serving quantities.
            Better logs give better insights.
          </p>
          <ul>
            <li>✓ Food search</li>
            <li>✓ Serving-based quantity</li>
            <li>✓ Daily tracking</li>
          </ul>
        </div>

        <div className="ngdash-card">
          <h3>👤 User Profile</h3>
          <p>
            Personalize your analysis with gender, age and health conditions
            for accurate targets.
          </p>
          <ul>
            <li>✓ Age and gender</li>
            <li>✓ Condition selection</li>
            <li>✓ Personalized targets</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default DashboardHome;